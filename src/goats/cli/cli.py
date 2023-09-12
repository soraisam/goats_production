__all__ = ["cli"]
# Standard library imports.
from pathlib import Path
import shutil
import subprocess
import platform
import json
from typing import IO, Any

# Related third party imports.
import click
from click._compat import get_text_stderr

# Local application/library specific imports.
from .modify_settings import modify_settings

MAC_PATH = Path.home() / "Library/Application Support/Google/Chrome/External Extensions"
LINUX_PATHS = [Path("/opt/google/chrome/extensions/"), Path("/usr/share/google-chrome/extensions/")]


class GOATSClickException(click.ClickException):
    """An extension of ClickException to show a goat emoji with the message."""

    def show(self, file: IO[Any] | None = None) -> None:
        """Display the error message prefixed with a goat emoji.

        If a file object is passed, it writes the message to the file,
        otherwise, it writes the message to standard error.

        Parameters
        ----------
        file : `IO[Any] | None`, optional
            The file object to write the message to, by default ``None``.
        """
        if file is None:
            file = get_text_stderr()

        click.echo(click.style(f"🐐 Error: {self.format_message()}", fg="red", bold=True), file=file)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Gemini Observation and Analysis of Targets System (GOATS).

    You can run each subcommand with its own options and arguments. For
    details on a specific command, type 'goats COMMAND --help'.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@click.command(help=("Installs GOATS."))
@click.option("-p", "--project-name", default="GOATS", type=str,
              help="Specify a custom project name. Default is 'GOATS'.")
@click.option("-d", "--directory", default=Path.cwd(), type=Path,
              help=("Specify the parent directory where GOATS will be installed. "
                    "Default is the current directory."))
@click.option("--overwrite", is_flag=True,
              help="Overwrite the existing project, if it exists. Default is False.")
def install(project_name: str, directory: Path | str, overwrite: bool) -> None:
    """Installs GOATS with a specified or default name in a specified or
    default directory.

    Parameters
    ----------
    project_name : `str`
        The name of the project to be created.
    directory : `Path | str`
        The directory where the project will be created.
    overwrite : `bool`
        Whether to overwrite the existing project if it exists, default is
        `False`.

    Raises
    ------
    GOATSClickException
        Raised if GOATS installation already exists and overwrite disabled.
    GOATSClickException
        Raised if the 'subprocess' calls fail.
    """
    project_path = directory / project_name

    # If directory and project exist, ask to remove.
    if (project_path).is_dir():
        if not overwrite:
            raise GOATSClickException(f"'{project_path.absolute()}' already exists. Use the "
                                      "'--overwrite' option to overwrite it.")
        shutil.rmtree(project_path)

    # If directory is provided, make sure it exists.
    directory.mkdir(parents=True, exist_ok=True)

    try:
        # Run the startproject command in the specified directory.
        subprocess.run(["django-admin", "startproject", project_name], cwd=directory, check=True)

        # Get the path for the 'settings.py' file.
        settings_file = project_path / project_name / "settings.py"

        # Add the TOM Toolkit plugin.
        modify_settings(settings_file, add_goats=True)

        # Get the path for the 'manage.py' file.
        manage_file = project_path / "manage.py"

        # Setup the TOM Toolkit.
        subprocess.run([f"{manage_file}", "goats_setup"], check=True)

        # Migrate the webpage.
        display_message("Wrapping up:", show_goats_emoji=False)
        display_info("Running final migrations... ")
        subprocess.run([f"{manage_file}", "migrate"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       check=True)
        display_ok()

        display_message("GOATS installed!", color="green")

    except subprocess.CalledProcessError as error:
        cmd_str = " ".join(error.cmd)
        raise GOATSClickException(f"🐐 An error occurred while running the command: '{cmd_str}'. Exit status:"
                                  f" {error.returncode}.", fg="red", bold=True)


@click.command(help=("Starts the server for GOATS."))
@click.option("-p", "--project-name", default="GOATS", type=str,
              help="Specify a custom project name. Default is 'GOATS'.")
@click.option("-d", "--directory", default=Path.cwd(), type=Path,
              help=("Specify the parent directory where GOATS is installed. "
                    "Default is the current directory."))
@click.option("--reloader", is_flag=True, help="Runs the server with reloader for active development.")
def run(project_name: str, directory: Path | str, reloader: bool) -> None:
    """Starts the server for GOATS.

    Parameters
    ----------
    project_name : `str`
        The name of the project to be started.
    directory : `Path | str`
        The directory where the project is installed.
    reloader : `bool`
        Runs the server with the reloader option enabled for active
        development.

    Raises
    ------
    GOATSClickException
        Raised if the 'manage.py' file for the project does not exist.
    GOATSClickException
        Raised if the 'subprocess' calls fail.
    """
    display_message("Serving GOATS.")
    display_message("Finding GOATS installation:", show_goats_emoji=False)
    display_info("Verifying 'manage.py' exists for GOATS...")
    project_path = directory / project_name
    # Get the path for the 'manage.py' file.
    manage_file = project_path / "manage.py"
    if not manage_file.is_file():
        display_failed()
        raise GOATSClickException(f"The 'manage.py' file for the project '{project_name}' does not at exist "
                                  f"at '{manage_file.absolute()}'.")
    display_ok()
    try:
        # Start the dev server, not meant for production.
        if reloader:
            subprocess.run([f"{manage_file}", "runserver_plus"], check=True)
        else:
            subprocess.run([f"{manage_file}", "runserver"], check=True)
    except subprocess.CalledProcessError as error:
        cmd_str = " ".join(error.cmd)
        raise GOATSClickException(f"An error occurred while running the command: '{cmd_str}'. Exit status: "
                                  f"{error.returncode}.")


@click.command(help="Installs the GOATS Chrome extension.")
def install_chrome_extension() -> None:
    """Install a Chrome extension from the Chrome Web Store.

    Raises
    ------
    GOATSClickException
        Raised if user does not want to install the extension.
    GOATSClickException
        Raised if Chrome extension directory not found on MacOS.
    GOATSClickException
        Raised if Chrome extension directory not found on Linux.
    GOATSClickException
        Raised if OS is Windows.
    """
    raise GOATSClickException("Not implemented yet. Requires extension to be hosted on Chrome Extension "
                              "Store.")
    display_message("Installing GOATS Chrome Extension.")

    if not click.confirm("Do you want to continue with the Chrome extension install?"):
        raise GOATSClickException("Aborting installation.")

    extension_id = "aapbdbdomjkkjkaonfhkkikfgjllcleb"

    display_message("Checking computer & browser requirements:", show_goats_emoji=False)
    system = platform.system()
    display_info("Checking OS system...")
    if system == "Darwin":  # Mac
        extension_dir = Path(MAC_PATH)

    elif system == "Linux":
        extension_dir = next((dir_path for dir_path in LINUX_PATHS if dir_path.exists()), None)

    else:
        display_failed()
        raise GOATSClickException("This command is not supported on Windows.")
    display_ok()

    display_info("Checking Chrome extension directory...")
    if extension_dir is None or not extension_dir.exists():
        display_failed()
        raise GOATSClickException("Chrome extension directory not found.")
    display_ok()

    display_info("Creating and installing extension preferences file...")
    # Create the JSON data
    extension_data = {"external_update_url": "https://clients2.google.com/service/update2/crx"}
    json_file_name = f"{extension_id}.json"
    json_file_path = extension_dir / json_file_name

    # Write JSON data to the file
    with json_file_path.open("w") as json_file:
        json.dump(extension_data, json_file, indent=2)
    display_ok()

    display_message("Success! GOATS Chrome extension installed.", color="green")
    display_message("Restart Google Chrome to complete the installation. Make sure to enable extension when "
                    "asked.")


def display_message(message: str, show_goats_emoji: bool = True, color: str = "cyan") -> None:
    """Displays a styled message to the console.

    Parameters
    ----------
    message : `str`
        The message to display.
    show_goats_emoji : `bool`, optional
        If ``False``, the goats emoji is not prefixed to the message, by
        default ``True``.
    """
    prefix = "🐐 " if show_goats_emoji else ""
    click.echo(click.style(f"{prefix}{message}", fg=color, bold=True))


def display_ok() -> None:
    """Display "OK" in green format."""
    click.echo(click.style("OK", fg="green", bold=True))


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
    click.echo(click.style("FAILED", fg="red", bold=True))


cli.add_command(install_chrome_extension)
cli.add_command(install)
cli.add_command(run)
