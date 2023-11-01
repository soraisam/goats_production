# Standard library imports.
from datetime import datetime
from io import StringIO
import json
from typing import Any
from urllib.parse import urlencode

# Related third party imports.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.management import call_command
from django.db import IntegrityError
from django.http import HttpResponse, HttpRequest
from django.forms import Form
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, View, FormView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils.safestring import mark_safe
from guardian.shortcuts import assign_perm
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from tom_alerts.alerts import get_service_class as tom_alerts_get_service_class
from tom_alerts.models import BrokerQuery
from tom_alerts.views import CreateTargetFromAlertView
from tom_common.hints import add_hint
from tom_common.mixins import SuperuserRequiredMixin, Raise403PermissionRequiredMixin
from tom_observations.facility import get_service_class as tom_facility_get_service_class
from tom_observations.models import ObservationRecord, ObservationTemplate
from tom_observations.observation_template import ApplyObservationTemplateForm
from tom_observations.views import AddExistingObservationView
from tom_targets.views import TargetDetailView

# Local application/library specific imports.
from .forms import GOAQueryForm, GOALoginForm
from .models import GOALogin
from .astroquery_gemini import Observations as GOA
from .utils import delete_associated_data_products


class GOATSCreateTargetFromAlertView(CreateTargetFromAlertView):
    """GOATS override to redirect to list view of targets."""

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handle POST request for creating targets from alerts. Redirects to
        the list view of targets if any target creation succeeds. Otherwise,
        redirects back to the alert view.

        Parameters
        ----------
        request : `HttpRequest`
            The request object.

        Returns
        -------
        `HttpResponse`
            Redirects to the list view of targets or back to the alert view
            based on the outcome of target creation.

        """
        query_id = self.request.POST["query_id"]
        broker_name = self.request.POST["broker"]
        broker_class = tom_alerts_get_service_class(broker_name)
        alerts = self.request.POST.getlist("alerts")
        errors = []
        if not alerts:
            messages.warning(request, "Please select at least one alert from which to create a target.")
            return redirect(reverse("tom_alerts:run", kwargs={"pk": query_id}))
        for alert_id in alerts:
            cached_alert = cache.get(f"alert_{alert_id}")
            if not cached_alert:
                messages.error(request, "Could not create targets. Try re running the query again.")
                return redirect(reverse("tom_alerts:run", kwargs={"pk": query_id}))
            generic_alert = broker_class().to_generic_alert(json.loads(cached_alert))
            target, extras, aliases = generic_alert.to_target()
            try:
                target.save(extras=extras, names=aliases)
                broker_class().process_reduced_data(target, json.loads(cached_alert))
                for group in request.user.groups.all().exclude(name="Public"):
                    assign_perm("tom_targets.view_target", group, target)
                    assign_perm("tom_targets.change_target", group, target)
                    assign_perm("tom_targets.delete_target", group, target)
            except IntegrityError:
                messages.warning(request, (f"Unable to save {target.name}, target with that name already"
                                           " exists."))
                errors.append(target.name)

        if (len(alerts) == len(errors)):
            return redirect(reverse("tom_alerts:run", kwargs={"pk": query_id}))

        return redirect(reverse("tom_targets:list"))


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


class GOATSTargetDetailView(TargetDetailView):
    """Extends TOMToolkit view to handle redirecting tab pane URL."""

    def get(self, request, *args, **kwargs):
        """
        Handles the GET requests to this view. If update_status is passed into
        the query parameters, calls the updatestatus management command to
        query for new statuses for ``ObservationRecord`` objects associated
        with this target.
        """
        update_status = request.GET.get("update_status", False)
        if update_status:
            if not request.user.is_authenticated:
                return redirect(reverse("login"))
            target_id = kwargs.get("pk", None)
            out = StringIO()
            call_command("updatestatus", target_id=target_id, stdout=out)
            messages.info(request, out.getvalue())
            add_hint(request, mark_safe(
                "Did you know updating observation statuses can be automated? Learn how in"
                "<a href=https://tom-toolkit.readthedocs.io/en/stable/customization/automation.html>"
                " the docs.</a>"))
            return redirect(reverse("tom_targets:detail", args=(target_id,)) + "?tab=observations")

        obs_template_form = ApplyObservationTemplateForm(request.GET)
        if obs_template_form.is_valid():
            obs_template = ObservationTemplate.objects.get(
                pk=obs_template_form.cleaned_data["observation_template"].id)
            obs_template_params = obs_template.parameters
            obs_template_params["cadence_strategy"] = request.GET.get("cadence_strategy", "")
            obs_template_params["cadence_frequency"] = request.GET.get("cadence_frequency", "")
            params = urlencode(obs_template_params)
            return redirect(
                reverse("tom_observations:create",
                        args=(obs_template.facility,)) + f"?target_id={self.get_object().id}&" + params)

        return super().get(request, *args, **kwargs)


class GOATSAddExistingObservationView(AddExistingObservationView):
    """Extends TOMToolkit view to handle redirecting tab pane URL."""

    def form_valid(self, form):
        """
        Runs after form validation. Creates a new ``ObservationRecord``
        associated with the specified target and facility.
        """
        records = ObservationRecord.objects.filter(target_id=form.cleaned_data["target_id"],
                                                   facility=form.cleaned_data["facility"],
                                                   observation_id=form.cleaned_data["observation_id"])

        if records and not form.cleaned_data.get("confirm"):
            return redirect(reverse("tom_observations:add-existing") + "?" + self.request.POST.urlencode())
        else:
            ObservationRecord.objects.create(
                target_id=form.cleaned_data["target_id"],
                facility=form.cleaned_data["facility"],
                parameters={},
                observation_id=form.cleaned_data["observation_id"]
            )
            observation_id = form.cleaned_data["observation_id"]
            messages.success(self.request, f"Successfully associated observation record {observation_id}")
        base_url = reverse("tom_targets:detail", kwargs={"pk": form.cleaned_data["target_id"]})
        query_params = urlencode({"tab": "observations"})
        return redirect(f"{base_url}?{query_params}")


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
            # Do something with form.cleaned_data
            service_class = tom_facility_get_service_class(form.cleaned_data["facility"])

            # Get GOA credentials.
            prop_data_msg = "Proprietary data will not be downloaded."
            try:
                goa_credentials = GOALogin.objects.get(user=request.user)
                # Login to GOA.
                GOA.login(goa_credentials.username, goa_credentials.password)
                if not GOA.authenticated():
                    raise PermissionError

            except GOALogin.DoesNotExist:
                messages.warning(request, f"GOA login credentials not found. {prop_data_msg}")
            except PermissionError:
                messages.warning(request, f"GOA login failed. Re-enter login credentials. {prop_data_msg}")

            # Must pass in product_id to avoid args and product_id issue.
            service_class().save_data_products(
                observation_record, query_params=form.cleaned_data["query_params"])
            # At the end of this, clear the cookies to prevent other users.
            GOA.logout()

        else:
            # Pass the form with errors to the template
            for field, errors in form.errors.items():
                for error in errors:
                    msg = f"Error in {field}: {error}"
                    messages.error(request, msg)

        return redirect(reverse(
            "tom_observations:detail",
            kwargs={"pk": kwargs["pk"]}
        ))


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
        user = User.objects.get(pk=self.kwargs["pk"])

        if request.user.is_superuser:
            Token.objects.filter(user=user).delete()  # Delete any existing token
            token, _ = Token.objects.get_or_create(user=user)
        else:
            # TODO: Should we issue an error and display it or just redirect?
            return reverse_lazy("user-list")

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
            messages.error(self.request, "Failed to verify GOA login credentials. Please try again.")
        else:
            GOA.logout()

            # Save to your model (update or create new)
            GOALogin.objects.update_or_create(
                user=user,
                defaults={"username": username, "password": password},
            )

            messages.success(self.request, "GOA login information verified and saved successfully.")
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
        messages.error(self.request, "Failed to save GOA login information. Please try again.")
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
