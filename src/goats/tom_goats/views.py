# Standard library imports.
from datetime import datetime
import json
from typing import Any

# Related third party imports.
from django.db import IntegrityError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from tom_alerts.alerts import get_service_class
from tom_alerts.models import BrokerQuery

# Local application/library specific imports.


@csrf_exempt
def receive_query(request: HttpResponse) -> HttpResponse:
    """Receive a query string and convert into target or query.

    Parameters
    ----------
    request : `HttpRequest`
        The HTTP request object.

    Returns
    -------
    HttpResponse
        A HTTP response indicating success or failure.
    """
    # Stop if not logged in and cookie is provided.
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

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
