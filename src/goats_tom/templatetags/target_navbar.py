"""
This module provides Django template tag for a navbar to use where context is missing.
"""

__all__ = ["render_target_navbar"]

from typing import Any

from django import template

register = template.Library()


@register.inclusion_tag("partials/target_navbar.html", takes_context=True)
def render_target_navbar(context: template.context.RequestContext) -> dict[str, Any]:
    """Provide the target navbar context.

    Parameters
    ----------
    context : `template.context.RequestContext`
        The `RequestContext` instance containing all the context used in rendering.

    Returns
    -------
    `dict[str, Any]`
        A dictionary representing the context to be passed to the target navigation bar
        template.
    """
    return {"target": context.get("target", {})}
