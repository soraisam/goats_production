# Standard library imports.
from datetime import datetime
import json
from typing import Any

# Related third party imports.
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from tom_alerts.alerts import get_service_class
from tom_alerts.models import BrokerQuery
from tom_common.mixins import SuperuserRequiredMixin
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# Local application/library specific imports.


class UserGenerateTokenView(SuperuserRequiredMixin, TemplateView):
    """A view that facilitates the generation of a token for a specific user,
    accessible only by superusers.

    Attributes
    ----------
    template_name : `str`
        The name of the template to be used in this view.
    """

    template_name = "auth/generate_token.html"

    def get(self, request, *args, **kwargs) -> HttpResponse:
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
            broker_class = get_service_class("ANTARES")()
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
                broker='ANTARES',
                parameters=query,
            )

            # Save the new BrokerQuery instance to the database.
            broker_query.save()
        else:
            # Not a recognized format.
            return HttpResponse(status=400)

        return HttpResponse(status=200)


def _generate_query_name() -> str:
    """Generates a unique name for query."""
    return f"esquery_ANTARES_{datetime.now().strftime('%Y%m%d%H%M%S')}"


def _is_single_target(data_dict: dict[str, Any]) -> bool:
    """Check if the given dictionary contains a single target query."""
    return "locusid" in data_dict


def _is_esquery(data_dict: dict[str, Any]) -> bool:
    """Check if the given dictionary contains elastic search query."""
    return "esquery" in data_dict
