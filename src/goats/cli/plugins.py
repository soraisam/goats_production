__all__ = ["Plugin", "TOMToolkitPlugin", "GeminiPlugin", "ANTARESPlugin", "GOATSPlugin"]
# Standard library imports.
from dataclasses import dataclass

# Related third party imports.

# Local application/library specific imports.


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
class GeminiPlugin(Plugin):
    """Gemini settings that extend the ``Plugin`` class."""

    name: str = "gemini"
    look_for: str = "TOM_FACILITY_CLASSES"
    line_to_add: str = "    'tom_gemini_community.gemini_gsselect.GEMFacility',\n"


@dataclass
class TOMToolkitPlugin(Plugin):
    """TOMToolkit settings that extend the ``Plugin`` class."""
    name: str = "tom"
    look_for: str = "INSTALLED_APPS"
    line_to_add: str = "    'tom_setup',\n"


@dataclass
class ANTARESPlugin(Plugin):
    """ANTARES settings that extend the ``Plugin`` class."""

    name: str = "antares"
    look_for: str = "TOM_ALERT_CLASSES"
    line_to_add: str = "    'tom_antares.antares.ANTARESBroker',\n"
    line_to_remove: str = "    'tom_alerts.brokers.antares.ANTARESBroker',\n"


@dataclass
class GOATSPlugin(Plugin):
    """GOATS settings the extend the ``Plugin`` class."""

    name: str = "goats"
    look_for: str = "INSTALLED_APPS"
    line_to_add: str = "    'goats.tom_goats',\n"
