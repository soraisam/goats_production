__all__ = ["cli"]
# Standard library imports.
from pathlib import Path
import shutil
import subprocess
import threading
from typing import IO, Any

# Related third party imports.
import click
from click._compat import get_text_stderr

# Local application/library specific imports.
from .modify_settings import modify_settings
from .modify_manage import modify_manage


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
@click.option("-m", "--media-dir", type=Path, help="Path for saving downloaded media.", default=None)
def install(project_name: str, directory: Path, overwrite: bool, media_dir: Path | None) -> None:
    """Installs GOATS with a specified or default name in a specified or
    default directory.

    Parameters
    ----------
    project_name : `str`
        The name of the project to be created.
    directory : `Path`
        The directory where the project will be created.
    overwrite : `bool`
        Whether to overwrite the existing project if it exists, default is
        `False`.
    media_dir : `Path | None`
        The path to save media files.

    Raises
    ------
    GOATSClickException
        Raised if GOATS installation already exists and overwrite disabled.
    GOATSClickException
        Raised if the 'subprocess' calls fail.
    GOATSClickException
        Raised if the 'media_dir' path is not writable.
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

        # Modify the manage file for Huey.
        modify_manage(manage_file)

        # Change the MEDIA_ROOT if provided.
        if media_dir:
            full_media_dir = media_dir / "data"
            if full_media_dir.exists():
                display_warning("Media root directory already exists, proceeding but existing data might "
                                "conflict.")

        # Setup the TOM Toolkit.
        goats_setup_command = [f"{manage_file}", "goats_setup"]
        if media_dir is not None:
            goats_setup_command.extend(["--media-dir", f"{media_dir}"])
        subprocess.run(goats_setup_command, check=True)

        # Migrate the webpage.
        display_message("Wrapping up:", show_goats_emoji=False)
        display_info("Running final migrations... ")
        subprocess.run([f"{manage_file}", "makemigrations"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       check=True)
        subprocess.run([f"{manage_file}", "migrate"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       check=True)
        display_ok()

        display_message("GOATS installed!", color="green")

    except subprocess.CalledProcessError as error:
        cmd_str = " ".join(error.cmd)
        raise GOATSClickException(f"An error occurred while running the command: '{cmd_str}'. Exit status:"
                                  f" {error.returncode}.")

    except Exception as error:
        raise GOATSClickException(str(error))


@click.command(help=("Starts the server and workers for GOATS."))
@click.option("-p", "--project-name", default="GOATS", type=str,
              help="Specify a custom project name. Default is 'GOATS'.")
@click.option("-d", "--directory", default=Path.cwd(), type=Path,
              help=("Specify the parent directory where GOATS is installed. "
                    "Default is the current directory."))
@click.option("-w", "--workers", default=3, type=int,
              help="Number of workers to spawn for background tasks.")
def run(project_name: str, directory: Path, workers: int) -> None:
    """Starts the server and workers for GOATS.

    Parameters
    ----------
    project_name : `str`
        The name of the project to be started.
    directory : `Path`
        The directory where the project is installed.
    workers : `int`
        The number of workers to spawn for background tasks.

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

    display_message("Starting GOATS and background workers:", show_goats_emoji=False)
    # Start Huey consumer in a separate thread
    huey_thread = threading.Thread(target=start_huey_consumer, args=(str(manage_file), workers))
    huey_thread.start()

    # Start Django server in a separate thread
    django_thread = threading.Thread(target=start_django_server, args=(str(manage_file),))
    django_thread.start()

    # Keep the main thread running while sub-threads are working
    django_thread.join()
    huey_thread.join()


def start_django_server(manage_file: Path) -> None:
    """Starts the Django development server.

    Parameters
    ----------
    manage_file : `Path`
        Path to the GOATS manage file.

    Raises
    ------
    GOATSClickException
        Raised if issue starting Django server.
    """
    try:
        subprocess.run([f"{manage_file}", "runserver"], check=True)
    except subprocess.CalledProcessError as error:
        raise GOATSClickException(f"Error running Django server: '{error.cmd}'. "
                                  f"Exit status: {error.returncode}.")


def start_huey_consumer(manage_file: Path, workers: int) -> None:
    """Starts the Huey consumer with "greenlet" workers.

    Parameters
    ----------
    manage_file : `Path`
        Path to the GOATS manage file.

    Raises
    ------
    GOATSClickException
        Raised if issue starting Huey consumers.
    """
    try:
        subprocess.run(
            [f"{manage_file}", "run_huey", "--workers", f"{workers}"], check=True)
    except subprocess.CalledProcessError as error:
        raise GOATSClickException(f"Error running Huey consumer: '{error.cmd}'. "
                                  f"Exit status: {error.returncode}.")


def display_message(message: str, show_goats_emoji: bool = True, color: str = "cyan") -> None:
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


def display_warning(message: str, indent: int = 0) -> None:
    """Display a message in yellow format for warnings.

    Parameters
    ----------
    message : `str`
        The message to be displayed.
    indent : `int`, optional
        The number of spaces for indentation, by default 0.
    """
    click.echo(click.style(f"🐐 WARNING: {' ' * indent}{message}", fg="yellow", bold=True))


cli.add_command(install)
cli.add_command(run)
