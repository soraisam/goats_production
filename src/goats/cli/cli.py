__all__ = ["cli"]
# Standard library imports.
from pathlib import Path
import shutil
import subprocess

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


@click.command()
@click.option("--project-name", default="GOATS", type=str,
              help="Specify a custom project name. Default is 'GOATS'.")
@click.option("--directory", default=Path.cwd(), type=Path,
              help=("Specify the parent directory where the project will be created. "
                    "Default is the current directory."))
@click.option("--overwrite", is_flag=True, help="Overwrite the existing project, if it exists.")
def install(project_name: str, directory: Path | str, overwrite: bool) -> None:
    """Creates a new Django project with a specified or default name in a
    specified or default directory.

    Parameters
    ----------
    project_name : `str`
        The name of the project to be created.
    directory : `Path` | `str`
        The directory where the project will be created.
    overwrite : `bool`
        Whether to overwrite the existing project if it exists.

    Raises
    ------
    click.ClickException
        Raised if the project already exists and the `overwrite` option is not
        set.
        Raised if the 'subprocess' calls fail.
        Raised if the TOM Toolkit installation is not completed.
    """
    project_path = directory / project_name

    # If directory and project exist, ask to remove.
    if (project_path).is_dir():
        if not overwrite:
            raise click.ClickException(f"'{project_path.absolute()}' already exists.\nUse the "
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
        modify_settings(settings_file, add_tom_toolkit=True)

        # Get the path for the 'manage.py' file.
        manage_file = project_path / "manage.py"

        # Setup the TOM Toolkit.
        subprocess.run([f"{manage_file}", "tom_setup"], check=True)

        # Add the Gemini and ANTARES plugin.
        modify_settings(settings_file, add_gemini=True, add_antares=True, add_goats=True)

        # Migrate the webpage.
        subprocess.run([f"{manage_file}", "migrate"], check=True)

    except subprocess.CalledProcessError as error:
        raise click.ClickException(error)
    except ValueError as error:
        # Raised if the TOM Toolkit wasn't finished installing.
        raise click.ClickException(error)


@click.command()
@click.option("--project-name", default="GOATS", type=str,
              help="Specify a custom project name. Default is 'GOATS'.")
@click.option("--directory", default=Path.cwd(), type=Path,
              help=("Specify the parent directory where the project will be created. "
                    "Default is the current directory."))
def run(project_name: str, directory: Path | str) -> None:
    """Starts the Django development server for a specified project in a
    specified or default directory.

    Parameters
    ----------
    project_name : `str`
        The name of the project to be started.
    directory : `Path` | `str`
        The directory where the project is located.

    Raises
    ------
    click.ClickException
        Raised if the 'manage.py' file for the project does not exist.
        Raised if the 'subprocess' calls fail.
    """
    project_path = directory / project_name
    # Get the path for the 'manage.py' file.
    manage_file = project_path / "manage.py"
    if not manage_file.is_file():
        raise click.ClickException(f"The 'manage.py' file for the project '{project_name}' "
                                   f"does not at exist at '{manage_file.absolute()}'.")
    try:
        # Start the dev server, not meant for production.
        subprocess.run([f"{manage_file}", "runserver"], check=True)
    except subprocess.CalledProcessError as error:
        raise click.ClickException(error)


cli.add_command(install)
cli.add_command(run)
