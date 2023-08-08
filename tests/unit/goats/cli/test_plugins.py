from goats.cli.plugins import Plugin, TOMToolkitPlugin, GeminiPlugin, ANTARESPlugin, GOATSPlugin


def test_plugin():
    plugin = Plugin(name="test_plugin", look_for="LOOK_FOR", line_to_add="ADD_THIS_LINE")

    assert plugin.name == "test_plugin"
    assert plugin.look_for == "LOOK_FOR"
    assert plugin.line_to_add == "ADD_THIS_LINE"
    assert plugin.line_to_remove is None


def test_gemini_plugin():
    gemini_plugin = GeminiPlugin()

    assert gemini_plugin.name == "gemini"
    assert gemini_plugin.look_for == "TOM_FACILITY_CLASSES"
    assert gemini_plugin.line_to_add == "    'tom_gemini_community.gemini_gsselect.GEMFacility',\n"
    assert gemini_plugin.line_to_remove is None


def test_tom_toolkit_plugin():
    tom_plugin = TOMToolkitPlugin()

    assert tom_plugin.name == "tom"
    assert tom_plugin.look_for == "INSTALLED_APPS"
    assert tom_plugin.line_to_add == "    'tom_setup',\n"
    assert tom_plugin.line_to_remove is None


def test_antares_plugin():
    antares_plugin = ANTARESPlugin()

    assert antares_plugin.name == "antares"
    assert antares_plugin.look_for == "TOM_ALERT_CLASSES"
    assert antares_plugin.line_to_add == "    'tom_antares.antares.ANTARESBroker',\n"
    assert antares_plugin.line_to_remove == "    'tom_alerts.brokers.antares.ANTARESBroker',\n"


def test_goats_plugin():
    goats_plugin = GOATSPlugin()

    assert goats_plugin.name == "goats"
    assert goats_plugin.look_for == "INSTALLED_APPS"
    assert goats_plugin.line_to_add == "    'goats.tom_goats',\n"
    assert goats_plugin.line_to_remove is None
