__all__ = ["cli"]
# Standard library imports.
from pathlib import Path
import shutil
import subprocess
import sys

# Related third party imports.
import click

# Local application/library specific imports.
from .modify_settings import modify_settings


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
    click.ClickException
        Raised if the project already exists and the `overwrite` option is not
        set.
        Raised if the 'subprocess' calls fail.
    """
    project_path = directory / project_name

    # If directory and project exist, ask to remove.
    if (project_path).is_dir():
        if not overwrite:
            click.echo(click.style(f"🐐 '{project_path.absolute()}' already exists. Use the "
                                   "'--overwrite' option to overwrite it.", fg="red", bold=True))
            sys.exit(1)
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
        click.echo(click.style("Wrapping up:", fg="cyan", bold=True))
        click.echo("  Running final migrations... ", nl=False)
        subprocess.run([f"{manage_file}", "migrate"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       check=True)
        click.echo(click.style("OK", fg="green", bold=True))

        click.echo(click.style("🐐 GOATS installed!", fg="green", bold=True))
        click.echo(click.style("🐐 Run 'goats run' to start GOATS.", fg="cyan", bold=True))

    except subprocess.CalledProcessError as error:
        cmd_str = " ".join(error.cmd)
        click.echo(click.style(f"🐐 An error occurred while running the command: '{cmd_str}'. Exit status: "
                               f"{error.returncode}.", fg="red", bold=True))
        sys.exit(1)


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
    click.ClickException
        Raised if the 'manage.py' file for the project does not exist.
        Raised if the 'subprocess' calls fail.
    """
    click.echo(click.style("🐐 Serving GOATS.", fg="cyan", bold=True))
    project_path = directory / project_name
    # Get the path for the 'manage.py' file.
    manage_file = project_path / "manage.py"
    if not manage_file.is_file():
        click.echo(click.style(f"🐐 The 'manage.py' file for the project '{project_name}' "
                               f"does not at exist at '{manage_file.absolute()}'.",
                               fg="red", bold=True))
        sys.exit(1)
    try:
        # Start the dev server, not meant for production.
        if reloader:
            subprocess.run([f"{manage_file}", "runserver_plus"], check=True)
        else:
            subprocess.run([f"{manage_file}", "runserver"], check=True)
    except subprocess.CalledProcessError as error:
        cmd_str = " ".join(error.cmd)
        click.style(f"🐐 An error occurred while running the command: '{cmd_str}'. Exit status: "
                    f"{error.returncode}.", fg="red", bold=True)
        sys.exit(1)


cli.add_command(install)
cli.add_command(run)
