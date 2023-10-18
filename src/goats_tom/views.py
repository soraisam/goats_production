# Standard library imports.
from datetime import datetime
import json
from typing import Any

# Related third party imports.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, View, FormView
from django.urls import reverse_lazy, reverse
from django.contrib import messages

from tom_alerts.alerts import get_service_class as tom_alerts_get_service_class
from tom_observations.facility import get_service_class as tom_facility_get_service_class
from tom_alerts.models import BrokerQuery
from tom_common.mixins import SuperuserRequiredMixin
from tom_observations.models import ObservationRecord

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# Local application/library specific imports.
from .forms import GOAQueryForm, GOALoginForm
from .models import GOALogin
from .astroquery_gemini import Observations as GOA


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
