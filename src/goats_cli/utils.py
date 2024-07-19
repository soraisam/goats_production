"""Utilities for CLI to use."""

__all__ = [
    "display_message",
    "display_ok",
    "display_info",
    "display_failed",
    "display_warning",
]
import time

import click


def display_message(
    message: str, show_goats_emoji: bool = True, color: str = "cyan"
) -> None:
    """Displays a styled message to the console.

    Parameters
    ----------
    message : `str`
        The message to display.
    show_goats_emoji : `bool`, optional
        If ``False``, the goats emoji is not prefixed to the message, by
        default ``True``.
    color : `str`
        The color to output the message in.

    """
    prefix = "🐐 " if show_goats_emoji else ""
    click.echo(click.style(f"{prefix}{message}", fg=color, bold=True))


def display_ok() -> None:
    """Display "OK" in green format."""
    time.sleep(0.5)
    click.echo(click.style(" OK", fg="green", bold=True))
    time.sleep(0.5)


def display_info(message: str, indent: int = 4) -> None:
    """Display a message with specified indentation.

    Parameters
    ----------
    message : `str`
        The message to be displayed.
    indent : `int`, optional
        The number of spaces for indentation, by default 4.

    """
    click.echo(f"{' ' * indent}{message}", nl=False)


def display_failed() -> None:
    """Display "FAILED" in red."""
    click.echo(click.style(" FAILED", fg="red", bold=True))


def display_warning(message: str, indent: int = 0) -> None:
    """Display a message in yellow format for warnings.

    Parameters
    ----------
    message : `str`
        The message to be displayed.
    indent : `int`, optional
        The number of spaces for indentation, by default 0.

    """
    click.echo(
        click.style(f"🐐 WARNING: {' ' * indent}{message}", fg="yellow", bold=True)
    )
