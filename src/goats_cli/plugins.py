"""Classes for plugins."""

__all__ = ["Plugin", "GOATSPlugin"]

from dataclasses import dataclass


@dataclass
class Plugin:
    """Used to modify and setup a plugin for use in TOMToolkit.

    Attributes
    ----------
    name : `str`
        The name of the plugin.
    look_for : `str`
        The string to search for in the settings file.
    line_to_add : `str`
        The line to be added to the settings file.
    line_to_remove : `str`, optional
        The line to be removed from the settings file, default is `None`.
    """

    name: str
    look_for: str
    line_to_add: str
    line_to_remove: str = None


@dataclass
class GOATSPlugin(Plugin):
    """Plugin to install GOATS."""

    name: str = "goats_setup"
    look_for: str = "INSTALLED_APPS"
    line_to_add: str = "    'goats_setup',\n"
