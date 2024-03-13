import json
from datetime import datetime
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core import serializers
from django.db import IntegrityError
from django.forms import Form
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, FormView, TemplateView, View
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from tom_alerts.alerts import get_service_class as tom_alerts_get_service_class
from tom_alerts.models import BrokerQuery
from tom_common.mixins import Raise403PermissionRequiredMixin, SuperuserRequiredMixin
from tom_dataproducts.forms import AddProductToGroupForm, DataProductUploadForm
from tom_dataproducts.views import DataProductDeleteView
from tom_observations.facility import BaseManualObservationFacility
from tom_observations.facility import (
    get_service_class as tom_observations_get_service_class,
)
from tom_observations.models import ObservationRecord
from tom_observations.views import ObservationRecordDetailView
from tom_targets.views import TargetDeleteView

from .astroquery import Observations as GOA
from .forms import GOALoginForm, GOAQueryForm, ProgramKeyForm, UserKeyForm
from .models import Download, GOALogin, ProgramKey, UserKey
from .tasks import download_goa_files
from .utils import build_json_response, delete_associated_data_products


@login_required
def activate_user_key(
    request: HttpRequest, user_pk: int, pk: int
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    """Activate a specified UserKey.

    Parameters
    ----------
    user_pk : `int`
        The primary key of the user.
    pk : `int`
        The primary key of the UserKey to be activated.

    Returns
    -------
    `HttpResponseRedirect | HttpResponsePermanentRedirect`
        Redirects to the manage-keys page.
    """
    key = get_object_or_404(UserKey, pk=pk)

    # Check permission: either the key belongs to the user or the user is a
    # superuser.
    if key.user.pk == request.user.pk or request.user.is_superuser:
        key.activate()
        messages.success(request, "Key activated.")
    else:
        messages.error(request, "You are not authorized to activate this key.")
        return redirect("manage-keys", pk=request.user.pk)

    return redirect("manage-keys", pk=user_pk)


@login_required
def create_key(
    request: HttpRequest, user_pk: int, key_type: str
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    """Create either a UserKey or a ProgramKey for a specific user.

    Parameters
    ----------
    request : `HttpRequest`
        The request object containing form data.
    user_pk : `int`
        The primary key of the user for whom the key is being created.
    key_type : `str`
        The type of key to be created ('user' or 'program').

    Returns
    -------
    `HttpResponseRedirect | HttpResponsePermanentRedirect`
        Redirects to the manage-keys page.
    """
    target_user = get_object_or_404(User, pk=user_pk)

    # Check if the logged-in user is the target user or a superuser.
    if request.user != target_user and not request.user.is_superuser:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("manage-keys", pk=request.user.pk)

    key_forms = {"user_key": UserKeyForm, "program_key": ProgramKeyForm}

    key_form = key_forms.get(key_type)

    # Redirect if key type is not found.
    if not key_form:
        messages.error(request, "Invalid key type specified.")
        return redirect("manage-keys", pk=user_pk)

    # Only handle 'POST'
    if request.method == "POST":
        form = key_form(request.POST, prefix=key_type)
        if form.is_valid():
            key = form.save(commit=False)
            key.user = target_user
            key.save()
            messages.success(
                request,
                f"{key_type.replace('_', ' ').capitalize()} created successfully.",
            )
        else:
            for error in form.errors.values():
                messages.error(request, error)

    return redirect("manage-keys", pk=user_pk)


@login_required
def delete_key(
    request: HttpRequest, user_pk: int, key_type: str, pk: int
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    """
    Delete a specified UserKey or ProgramKey for a given user.

    Parameters
    ----------
    request : `HttpRequest`
        The request object.
    user_pk : `int`
        The primary key of the user specified in the URL.
    key_type : `str`
        The type of key to delete ('user_key' or 'program_key').
    pk : `int`
        The primary key of the key to be deleted.

    Returns
    -------
    `HttpResponseRedirect | HttpResponsePermanentRedirect`
        Redirects to the manage-keys page after deletion.
    """
    key_models = {"user_key": UserKey, "program_key": ProgramKey}
    model = key_models.get(key_type)

    # Redirect if key type not found.
    if not model:
        messages.error(request, "Invalid key type specified.")
        return redirect("manage-keys", pk=user_pk)

    key = get_object_or_404(model, pk=pk)

    # Check permission: either the key belongs to the user or the user is a
    # superuser.
    if key.user.pk == request.user.pk or request.user.is_superuser:
        key.delete()
        messages.success(
            request, f"{key_type.replace('_', ' ').capitalize()} deleted successfully."
        )
    else:
        messages.error(request, "You do not have permission to delete this key.")
        return redirect("manage-keys", pk=request.user.pk)

    return redirect("manage-keys", pk=user_pk)


class ManageKeysView(LoginRequiredMixin, TemplateView):
    """A Django view for managing User and Program Keys."""

    template_name = "auth/manage_keys.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the user_pk from URL kwargs, default to the logged-in user if not
        # provided.
        user_pk = self.kwargs.get("pk", self.request.user.pk)

        # Fetch the user object. If user_pk is not found, a 404 response will
        # be triggered.
        target_user = get_object_or_404(User, pk=user_pk)

        # Update the context with the target user and their keys
        context["target_user"] = target_user
        context["user_key_form"] = UserKeyForm(prefix="user_key")
        context["program_key_form"] = ProgramKeyForm(prefix="program_key")
        context["user_keys"] = UserKey.objects.filter(user=target_user)
        context["program_keys"] = ProgramKey.objects.filter(user=target_user)
        context["sites"] = ["GN", "GS"]
        return context


class GOATSTargetDeleteView(TargetDeleteView):
    def form_valid(self, form: Form) -> HttpResponse:
        """Handle deletion of associated observation records upon valid form
        submission.

        Parameters
        ----------
        form : `Form`
            The form object.

        Returns
        -------
        `HttpResponse`
            HTTP response indicating the outcome of the deletion process.
        """
        target = self.get_object()
        # Fetch the ObservationRecord object.
        observation_records = ObservationRecord.objects.filter(target=target)
        for observation_record in observation_records:
            # Delete the observation data products.
            delete_associated_data_products(observation_record)
            # Delete the observation record itself.
            observation_record.delete()

        # Proceed with deletion of the object.
        return super().form_valid(form)


def update_brokerquery_name(request: HttpRequest, pk: int) -> JsonResponse:
    """
    Update the name of a BrokerQuery object.

    Parameters
    ----------
    request : `HttpRequest`
        The incoming HTTP request.
    pk : `int`
        The ID of the BrokerQuery to be updated.

    Returns
    -------
    `JsonResponse`
        A JSON response indicating the status of the update operation. Returns
        a 200 status code if the update is successful. Returns an error message
        with a 404 status code if the query is not found, and with a 400 status
        code for any other invalid request.

    """
    if request.method == "POST":
        new_name = request.POST.get("name")

        try:
            query = BrokerQuery.objects.get(pk=pk)
            query.name = new_name
            # Need to update query_name to show in form.
            query.parameters["query_name"] = new_name
            query.save()
            return build_json_response()

        except BrokerQuery.DoesNotExist:
            return build_json_response("Query not found", status.HTTP_404_NOT_FOUND)

    return build_json_response("Invalid request", status.HTTP_400_BAD_REQUEST)


def recent_downloads(request: HttpRequest) -> HttpResponse:
    """Handle requests to the recent downloads page, displaying a list of
    completed downloads.

    Fetches all completed `Download` instances, sorted by start time in
    descending order, and renders them to the 'recent_downloads.html' template.

    Parameters
    ----------
    request : `HttpRequest`
        The HTTP request object.

    Returns
    -------
    `HttpResponse`
        The rendered HTML response containing the recent downloads.
    """
    # Fetch all Download instances
    downloads = Download.objects.filter(done=True).order_by("-start_time")

    # Pass the tasks to the template
    context = {"downloads": downloads}
    return render(request, "recent_downloads.html", context)


def ongoing_tasks(request: HttpRequest) -> JsonResponse:
    """Provide a JSON response with a list of ongoing downloads.

    Fetches all ongoing `Download` instances that are not marked as done.

    Parameters
    ----------
    request : `HttpRequest`
        The HTTP request object.

    Returns
    -------
    `JsonResponse`
        A JSON response containing the ongoing tasks.
    """
    # First, evaluate the QuerySet and get the current tasks data
    tasks = list(
        Download.objects.filter(done=False).values("unique_id", "observation_id")
    )

    # Return the evaluated tasks list
    return JsonResponse(tasks, safe=False)


class GOATSObservationRecordDetailView(ObservationRecordDetailView):
    """View to override creating thumbnails."""

    def get_context_data(self, *args, **kwargs):
        """Override for avoiding "get_preview" and creating thumbnail."""
        context = super(DetailView, self).get_context_data(*args, **kwargs)
        context["form"] = AddProductToGroupForm()
        facility = tom_observations_get_service_class(self.object.facility)()
        facility.set_user(self.request.user)
        observation_record = self.get_object()

        context["editable"] = isinstance(facility, BaseManualObservationFacility)
        context["data_products"] = facility.all_data_products(self.object)
        context["can_be_cancelled"] = (
            self.object.status not in facility.get_terminal_observing_states()
        )
        context["target"] = observation_record.target
        data_product_upload_form = DataProductUploadForm(
            initial={
                "observation_record": observation_record,
                "referrer": reverse(
                    "tom_observations:detail", args=(self.get_object().id,)
                ),
            }
        )
        context["data_product_form"] = data_product_upload_form
        return context


class DeleteObservationDataProductsView(Raise403PermissionRequiredMixin, View):
    """A view for handling the deletion of all data products associated with a
    specific observation.

    This view extends `Raise403PermissionRequiredMixin` to include permission
    checks based on the application's settings.
    """

    template_name = (
        "tom_observations/observationrecord_dataproducts_confirm_delete.html"
    )
    # Share same permission since deleting all data products for observation.
    permission_required = "tom_observations.delete_dataproduct"

    def get_required_permissions(
        self, request: HttpRequest | None = None
    ) -> list[str] | None:
        """Get the required permissions for this view.

        Parameters
        ----------
        request : `HttpRequest`, optional
            The `HttpRequest` object.

        Returns
        -------
        `list[str] | None`
            A list of required permission strings, or ``None`` if custom
            settings apply.
        """
        if settings.TARGET_PERMISSIONS_ONLY:
            # Custom logic based on your application's settings
            return None
        return super().get_required_permissions(request)

    def check_permissions(self, request: HttpRequest) -> bool:
        """Check if the request has the required permissions.

        Parameters
        ----------
        request : `HttpRequest`
            The `HttpRequest` object.

        Returns
        -------
        `bool`
            ``True`` if the request has the required permissions, ``False``
            otherwise.
        """
        if settings.TARGET_PERMISSIONS_ONLY:
            # Custom logic based on your application's settings
            return False
        return super().check_permissions(request)

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Handle the GET request to show the confirmation page.

        Parameters
        ----------
        request : `HttpRequest`
            The `HttpRequest` object.
        pk : `int`
            The ID of the observation record.

        Returns
        -------
        `HttpResponse`
            The HttpResponse object rendering the confirmation page.
        """
        observation_record = get_object_or_404(ObservationRecord, pk=pk)
        context = {
            "object": observation_record,
        }
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Handle the POST request to delete data products.

        Parameters
        ----------
        request : `HttpRequest`
            The `HttpRequest` object.
        pk : `int`
            The ID of the observation record.

        Returns
        -------
        `HttpResponse`
            Redirects to the observation detail page after deletion.
        """
        observation_record = get_object_or_404(ObservationRecord, pk=pk)
        try:
            delete_associated_data_products(observation_record)
            messages.success(request, "Data products deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error during deletion: {e}")

        return redirect(reverse("tom_observations:detail", args=[pk]))


class GOATSDataProductDeleteView(DataProductDeleteView):
    def form_valid(self, form):
        """
        Method that handles DELETE requests for this view. It performs the
        following actions in order:
        1. Deletes all ``ReducedDatum`` objects associated with the
        ``DataProduct``.
        2. Deletes the file referenced by the ``DataProduct``.
        3. Deletes the ``DataProduct`` object from the database.

        :param form: Django form instance containing the data for the DELETE
        request.
        :type form: django.forms.Form
        :return: HttpResponseRedirect to the success URL.
        :rtype: HttpResponseRedirect
        """
        # Fetch the DataProduct object
        data_product = self.get_object()
        delete_associated_data_products(data_product)

        return HttpResponseRedirect(self.get_success_url())


class ObservationRecordDeleteView(Raise403PermissionRequiredMixin, DeleteView):
    """View for deleting an observation."""

    permission_required = "tom_observations.delete_observationrecord"
    success_url = reverse_lazy("observations:list")
    model = ObservationRecord

    def form_valid(self, form: Form) -> HttpResponse:
        """Handle deletion of associated DataProducts upon valid form
        submission.

        Parameters
        ----------
        form : `Form`
            The form object.

        Returns
        -------
        `HttpResponse`
            HTTP response indicating the outcome of the deletion process.
        """
        # Fetch the ObservationRecord object.
        observation_record = self.get_object()
        delete_associated_data_products(observation_record)

        return super().form_valid(form)


class GOAQueryFormView(View):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handle POST requests.

        Parameters
        ----------
        request : `HttpRequest`
            The request object.

        Returns
        -------
        `HttpResponse`
            The response object.
        """
        # Check if your GOAQueryForm was submitted.
        form = GOAQueryForm(request.POST)
        observation_record = ObservationRecord.objects.get(pk=kwargs["pk"])
        if form.is_valid():
            # Get GOA credentials.
            prop_data_msg = "Proprietary data will not be downloaded."
            try:
                goa_credentials = GOALogin.objects.get(user=request.user)
                # Login to GOA.
                GOA.login(goa_credentials.username, goa_credentials.password)
                if not GOA.authenticated():
                    raise PermissionError
                GOA.logout()

            except GOALogin.DoesNotExist:
                messages.warning(
                    request, f"GOA login credentials not found. {prop_data_msg}"
                )
            except PermissionError:
                messages.warning(
                    request,
                    f"GOA login failed. Re-enter login credentials. {prop_data_msg}",
                )

            query_params = form.cleaned_data["query_params"]

            serialized_observation_record = serializers.serialize(
                "json", [observation_record]
            )
            # Download in background.
            download_goa_files(
                serialized_observation_record, query_params, request.user
            )
            messages.info(request, "Downloading data in background. Check back soon!")

        else:
            # Pass the form with errors to the template
            for field, errors in form.errors.items():
                for error in errors:
                    msg = f"Error in {field}: {error}"
                    messages.error(request, msg)

        return redirect(reverse("tom_observations:detail", kwargs={"pk": kwargs["pk"]}))


class UserGenerateTokenView(SuperuserRequiredMixin, TemplateView):
    """A view that facilitates the generation of a token for a specific user,
    accessible only by superusers.

    Attributes
    ----------
    template_name : `str`
        The name of the template to be used in this view.
    """

    template_name = "auth/generate_token.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handles the GET request to generate a token for a user.

        If the user making the request is a superuser, any existing tokens
        associated with the user identified by the primary key in the URL are
        deleted and a new token is generated.

        Parameters
        ----------
        request : `HttpRequest`
            The request instance.

        Returns
        -------
        `HttpResponse`
            A response instance containing the rendered template with user and
            token context, or a URL pointing to the "user-list" view if the
            requester is not a superuser.
        """
        try:
            user = User.objects.get(pk=self.kwargs["pk"])
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("user-list")

        if not request.user.is_superuser:
            messages.error(
                request, "You do not have permission to generate a token for this user."
            )
            return redirect("user-list")

        # Superuser logic for generating token
        Token.objects.filter(user=user).delete()
        token, _ = Token.objects.get_or_create(user=user)
        return render(request, self.template_name, {"user": user, "token": token})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def receive_query(request: HttpResponse) -> HttpResponse:
    """Receive a query string and convert into target or query.

    Parameters
    ----------
    request : `HttpRequest`
        The HTTP request object.

    Returns
    -------
    `HttpResponse`
        A HTTP response indicating success or failure.
    """
    data = request.body.decode("utf-8")

    if data:
        try:
            # Attempt to parse the query data as JSON.
            query = json.loads(data)
        except json.JSONDecodeError:
            # Payload cannot be loaded.
            return HttpResponse(status=400)

        if _is_single_target(query):
            # Get the class responsible for handling ANTARES broker service.
            broker_class = tom_alerts_get_service_class("ANTARES")()
            # Fetch alert based on the parsed query.
            alert = list(broker_class.fetch_alerts(query))[0]
            # Convert the generic alert into target format.
            generic_alert = broker_class.to_generic_alert(alert)
            target, extras, aliases = generic_alert.to_target()
            try:
                target.save(extras=extras, names=aliases)
            except IntegrityError:
                # Duplicate entry.
                return HttpResponse(status=409)

        elif _is_esquery(query):
            # Create a new query.
            broker_query = BrokerQuery.objects.create(
                name=_generate_query_name(),
                broker="ANTARES",
                parameters=query,
            )

            # Save the new BrokerQuery instance to the database.
            broker_query.save()
        else:
            # Not a recognized format.
            return HttpResponse(status=400)

        return HttpResponse(status=200)

    return HttpResponse(status=404)


class GOALoginView(LoginRequiredMixin, FormView):
    """View to handle GOA Login form."""

    template_name = "auth/goa_login.html"
    form_class = GOALoginForm

    def get_success_url(self) -> str:
        """Get the URL to redirect to on successful form submission.

        Returns
        -------
        `str`
            The URL to redirect to.
        """
        return reverse_lazy("user-list")

    def form_valid(self, form: GOALoginForm) -> HttpResponse:
        """Handle valid form submission.

        Parameters
        ----------
        form : `GOALoginForm`
            Valid form object.

        Returns
        -------
        `HttpResponse`
            HTTP response.
        """
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = get_object_or_404(User, pk=self.kwargs["pk"])

        # Test logging in to GOA.
        GOA.login(username, password)
        if not GOA.authenticated():
            messages.error(
                self.request,
                "Failed to verify GOA login credentials. Please try again.",
            )
        else:
            messages.success(
                self.request, "GOA login information verified and saved successfully."
            )

        # No matter what, logout and save credentials.
        GOA.logout()

        GOALogin.objects.update_or_create(
            user=user,
            defaults={"username": username, "password": password},
        )

        return super().form_valid(form)

    def form_invalid(self, form: GOALoginForm) -> HttpResponse:
        """Handle invalid form submission.

        Parameters
        ----------
        form : `GOALoginForm
            Invalid form object.

        Returns
        -------
        `HttpResponse`
            HTTP response.
        """
        messages.error(
            self.request, "Failed to save GOA login information. Please try again."
        )
        return super().form_invalid(form)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handle GET requests.

        Parameters
        ----------
        request : `HttpRequest`
            Incoming request object.

        Returns
        -------
        `HttpResponse`
            Rendered template as HTTP response.
        """
        user = User.objects.get(pk=self.kwargs["pk"])
        form = self.form_class()

        return render(request, self.template_name, {"user": user, "form": form})


def _generate_query_name() -> str:
    """Generates a unique name for query."""
    return f"esquery_ANTARES_{datetime.now().strftime('%Y%m%d%H%M%S')}"


def _is_single_target(data_dict: dict[str, Any]) -> bool:
    """Check if the given dictionary contains a single target query."""
    return "locusid" in data_dict


def _is_esquery(data_dict: dict[str, Any]) -> bool:
    """Check if the given dictionary contains elastic search query."""
    return "esquery" in data_dict
