__all__ = ["recent_downloads"]
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import render

from goats_tom.models import Download


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
