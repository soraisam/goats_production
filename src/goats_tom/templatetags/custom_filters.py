__all__ = ["starts_with"]
# Standard library imports.

# Related third party imports.
from django import template

# Local application/library specific imports.

register = template.Library()


@register.filter(name="starts_with")
def starts_with(text: str, look_for: str) -> bool:
    """Checks to see if string starts with provided text.

    Parameters
    ----------
    text : `str`
        The text to analyze.
    starts : `str`
        The string to look for at the beginning of the text.

    Returns
    -------
    `bool`
        `True` if text starts with string, `False` if not.

    """
    if isinstance(text, str):
        return text.startswith(look_for)

    return False
