import pytest
from pathlib import Path
import shutil
from goats.cli.modify_settings import modify_settings
from goats.cli.plugins import TOMToolkitPlugin, GeminiPlugin, ANTARESPlugin, GOATSPlugin


@pytest.fixture
def settings_file(tmp_path):
    settings_file = Path(__file__).parent.parent.parent / "data" / "settings.py"
    copied_settings_file = tmp_path / "settings.py"

    shutil.copyfile(settings_file, copied_settings_file)
    return copied_settings_file


@pytest.fixture
def tom_setup_settings_file(tmp_path):
    tom_setup_settings_file = Path(__file__).parent.parent.parent / "data" / "tom_setup_settings.py"
    copied_tom_setup_settings_file = tmp_path / "tom_setup_settings.py"

    shutil.copyfile(tom_setup_settings_file, copied_tom_setup_settings_file)
    return copied_tom_setup_settings_file


def test_modify_settings_tom_toolkit(tmp_path, settings_file):
    # Test adding tom toolkit plugin.
    modify_settings(settings_file, add_tom_toolkit=True)
    with open(settings_file, "r") as f:
        lines = f.readlines()
    assert TOMToolkitPlugin().line_to_add in lines

    # Test FileNotFoundError
    with pytest.raises(FileNotFoundError):
        modify_settings(tmp_path / "non_existent_settings.py")


def test_modify_settings_gemini(tom_setup_settings_file):
    # Test adding Gemini plugin.
    modify_settings(tom_setup_settings_file, add_gemini=True)
    with open(tom_setup_settings_file, "r") as f:
        lines = f.readlines()
    assert GeminiPlugin().line_to_add in lines


def test_modify_settings_antares(tom_setup_settings_file):
    # Test adding ANTARES plugin.
    modify_settings(tom_setup_settings_file, add_antares=True)
    with open(tom_setup_settings_file, "r") as f:
        lines = f.readlines()
    assert ANTARESPlugin().line_to_add in lines


def test_modify_settings_goats(tom_setup_settings_file):
    # Test adding ANTARES plugin.
    modify_settings(tom_setup_settings_file, add_goats=True)
    with open(tom_setup_settings_file, "r") as f:
        lines = f.readlines()
    assert GOATSPlugin().line_to_add in lines
