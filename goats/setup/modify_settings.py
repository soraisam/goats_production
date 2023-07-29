__all__ = ["modify_settings"]
# Standard library imports.
import argparse
from pathlib import Path

# Related third party imports.

# Local application/library specific imports.
from plugins import Plugin, TOMToolkitPlugin, GeminiPlugin, ANTARESPlugin


# Initialize constants.
SETTINGS_FILENAME = "settings.py"


def modify_settings(file_path: Path | str, add_tom_toolkit: bool = False, add_gemini: bool = False,
                    add_antares: bool = False) -> None:
    """Modify Django settings to include additional apps.

    Parameters
    ----------
    file_path : `Path | str`
        The path to the settings file that needs to be modified.
    add_tom_toolkit : `bool`, optional
        Flag indicating if TOMToolkit plugin should be added to settings.
    add_gemini : `bool`, optional
        Flag indicating if Gemini GSSelect plugin should be added to settings.
    add_antares : `bool`, optional
        Flag indicating if LSST Antares plugin should be added to settings.

    Raises
    ------
    FileNotFoundError
        Raised if the settings file does not exist.
    """
    print(f"Modifying {file_path.absolute()}...")

    # Convert to path object if it isn't.
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    # Check if file exists and raise if not.
    if not file_path.is_file():
        raise FileNotFoundError(f"{settings_file.absolute()} does not exist.")

    # Read the file.
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Add plugins.
    if add_tom_toolkit:
        lines = _find_and_add(lines, TOMToolkitPlugin())
    if add_gemini or add_antares:
        _verify_tom_setup(lines)
    if add_gemini:
        lines = _find_and_add(lines, GeminiPlugin())
    if add_antares:
        lines = _find_and_add(lines, ANTARESPlugin())

    # Write the file back out
    with open(file_path, "w") as f:
        f.writelines(lines)


def _verify_tom_setup(lines: list[str]) -> None:
    """Verifies that the TOMToolkit was finished successfully.

    Parameters
    ----------
    lines : `list[str]`
        The lines from the settings file.

    Raises
    ------
    ValueError
        Raised if the TOMToolkit setup was not completed.
    """
    tom_plugin = TOMToolkitPlugin()
    if tom_plugin.line_to_add.strip() in (line.strip() for line in lines):
        raise ValueError("TOMToolkit setup not completed, please finish TOM setup.")


def _find_and_add(lines: list[str], plugin: Plugin) -> list[str]:
    """Utility function to add a plugin to the lines from a settings file.

    Parameters
    ----------
    lines : `list[str]`
        The lines from the settings file.
    plugin: `Plugin`
        Class instance of the specific plugin to install.

    Returns
    -------
    `list[str]`
        The updated list of lines with the plugin added.

    Raises
    ------
    ValueError
        Raised if the ``Plugin.look_for`` string is not found in the file.
    """
    line_number = None

    # Don't change anything if already exists.
    if plugin.line_to_add.strip() in (line.strip() for line in lines):
        print(f"Plugin '{plugin.name}' already added...")
        return lines

    # Remove line if specified and exists
    if plugin.line_to_remove and plugin.line_to_remove.strip() in (line.strip() for line in lines):
        lines.remove(plugin.line_to_remove)
        print(f"Line removed for plugin '{plugin.name}'.")

    # Find line number for matching string.
    for index, line in enumerate(lines):
        if plugin.look_for in line:
            line_number = index
            break

    if line_number is None:
        raise ValueError(f"'{plugin.look_for}' not found in file, please verify contents.")

    # Find the opening bracket line.
    pointer = None
    for index, line in enumerate(lines[line_number:]):
        if "[" in line:
            pointer = index + line_number
            break

    # Insert just after the opening bracket.
    lines.insert(pointer + 1, plugin.line_to_add)

    print(f"Plugin '{plugin.name}' added.")
    return lines


if __name__ == "__main__":
    # Initialize argument parser.
    parser = argparse.ArgumentParser(
        description=f"Modify Django {SETTINGS_FILENAME} to include additional plugins.")
    parser.add_argument("directory", help=f"Path to directory that has Django {SETTINGS_FILENAME} file",
                        type=Path)
    parser.add_argument("--add-tom-toolkit", action="store_true",
                        help=f"Configure {SETTINGS_FILENAME} for TOMToolkit.")
    parser.add_argument("--add-gemini", action="store_true",
                        help=f"Configure {SETTINGS_FILENAME} for Gemini GSSelect.")
    parser.add_argument("--add-antares", action="store_true",
                        help=f"Configure {SETTINGS_FILENAME} for Antares Alert Broker.")
    args = parser.parse_args()

    # Build path for settings file.
    settings_file = args.directory / args.directory.name / SETTINGS_FILENAME

    modify_settings(settings_file, args.add_tom_toolkit, args.add_gemini, args.add_antares)
