from goats.cli.plugins import Plugin, GOATSPlugin


def test_plugin():
    plugin = Plugin(name="test_plugin", look_for="LOOK_FOR", line_to_add="ADD_THIS_LINE")

    assert plugin.name == "test_plugin"
    assert plugin.look_for == "LOOK_FOR"
    assert plugin.line_to_add == "ADD_THIS_LINE"
    assert plugin.line_to_remove is None


def test_goats_plugin():
    goats_plugin = GOATSPlugin()

    assert goats_plugin.name == "goats_setup"
    assert goats_plugin.look_for == "INSTALLED_APPS"
    assert goats_plugin.line_to_add == "    'goats.goats_setup',\n"
    assert goats_plugin.line_to_remove is None
