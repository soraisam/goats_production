__all__ = ["ongoing_tasks"]
from django.http import (
    HttpRequest,
    JsonResponse,
)

from goats_tom.models import Download


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
        Download.objects.filter(done=False).values("unique_id", "observation_id"),
    )

    # Return the evaluated tasks list
    return JsonResponse(tasks, safe=False)
