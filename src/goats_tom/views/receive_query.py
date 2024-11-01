__all__ = ["receive_query"]

import json
from datetime import datetime
from typing import Any

from django.db import IntegrityError
from django.http import (
    HttpResponse,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from tom_alerts.alerts import get_service_class as tom_alerts_get_service_class
from tom_alerts.models import BrokerQuery


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


def _generate_query_name() -> str:
    """Generates a unique name for query."""
    return f"esquery_ANTARES_{datetime.now().strftime('%Y%m%d%H%M%S')}"


def _is_single_target(data_dict: dict[str, Any]) -> bool:
    """Check if the given dictionary contains a single target query."""
    return "locusid" in data_dict


def _is_esquery(data_dict: dict[str, Any]) -> bool:
    """Check if the given dictionary contains elastic search query."""
    return "esquery" in data_dict
