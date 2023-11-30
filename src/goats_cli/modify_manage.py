__all__ = ["modify_manage"]
from pathlib import Path

MANAGE_FILENAME = "manage.py"


def modify_manage(file_path: Path | str) -> None:
    """Modify Django manage to include monkey patch for Huey.

    Parameters
    ----------
    file_path : Path | str
        The path to the settings file that needs to be modified.

    Raises
    ------
    FileNotFoundError
        Raised if the manage file does not exist.
    """

    # Convert to path object if it isn't.
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    # Check if file exists and raise if not.
    if not file_path.is_file():
        raise FileNotFoundError(f"{file_path.absolute()} does not exist.")

    # Read the file.
    with open(file_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if "import sys" in line:
            # Insert the monkey patch lines after 'import sys' line
            lines.insert(i + 1, "\n# Apply monkey-patch if we are running the huey consumer.\n")
            lines.insert(i + 2, "if 'run_huey' in sys.argv:\n")
            lines.insert(i + 3, "    from gevent import monkey\n")
            lines.insert(i + 4, "    monkey.patch_all()\n")
            break

    with open(file_path, 'w') as f:
        f.writelines(lines)
