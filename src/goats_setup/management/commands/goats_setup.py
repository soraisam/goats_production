from tom_setup.management.commands.tom_setup import Command as TOMCommand
import sys
from pathlib import Path
from packaging import version
from django.conf import settings
from django.template.loader import get_template
from django.utils import timezone
from django.core.management.utils import get_random_secret_key
from django.core.management import call_command
from django.contrib.auth.models import Group, User

PYTHON_VERSION = "3.10"


class Command(TOMCommand):
    """Setup wizard for GOATS.

    This class extends TOMCommand to provide a setup wizard for new GOATS
    projects.
    """
    help = "🐐 GOATS setup wizard."

    def welcome_banner(self) -> None:
        """Displays a welcome banner."""
        welcome_text = ("🐐 Welcome to the GOATS setup wizard. This will assist you with your "
                        "new GOATS project.\n")
        prompt = "Proceed with GOATS setup? [y/N] "
        self.stdout.write(self.style.MIGRATE_HEADING(welcome_text))

        # Reusing the prompt logic from the original class
        while True:
            response = input(prompt).lower()
            if not response or response == "n":
                self.stdout.write()
                self.exit(self.style.ERROR("Aborting installation."), return_code=1)
            elif response == "y":
                break
            else:
                self.stdout.write("Invalid response. Please try again.")

    def exit(self, msg: str, return_code: int = 0) -> None:
        """Exit the script.

        Parameters
        ----------
        msg : `str`
            The exit message to display.
        return_code : `int`, optional
            The exit code, default is 0.
        """
        self.stdout.write(f"🐐 {msg}")
        sys.exit(return_code)

    def add_arguments(self, parser):
        """Add custom command arguments."""
        super().add_arguments(parser)
        parser.add_argument(
            "--media-dir",
            type=str,
            help="Path where the data directory will be created."
        )

    def check_python(self) -> None:
        """Checks the Python version, exits if not compatible."""
        self.status("  Checking Python version... ")
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        if version.parse(current_version) < version.parse(PYTHON_VERSION):
            self.exit(self.style.ERROR(f"Incompatible Python version found. Please install Python >= "
                                       f"{PYTHON_VERSION}"), return_code=1)
        self.ok()

    def complete(self) -> None:
        """Exits with a 0 return code."""
        sys.exit()

    def generate_config(self) -> None:
        """Generates the settings.py file."""
        self.status("  Generating settings.py... ")
        template = get_template("goats_setup/settings.tmpl")
        rendered = template.render(self.context)

        settings_location = settings.BASE_DIR / settings.BASE_DIR.name / "settings.py"
        if not settings_location.exists():
            msg = ("Could not determine settings.py location. Writing settings.py out to "
                   f"{settings_location}. Please copy file to the proper location after script finishes.")
            self.stdout.write(self.style.WARNING(msg))
        with open(settings_location, "w+") as settings_file:
            settings_file.write(rendered)

        self.ok()

    def generate_urls(self) -> None:
        """Generates the urls.py file."""
        self.status("  Generating urls.py... ")
        template = get_template("goats_setup/urls.tmpl")
        rendered = template.render(self.context)

        urls_location = settings.BASE_DIR / settings.BASE_DIR.name / "urls.py"
        if not urls_location.exists():
            msg = (f"Could not determine urls.py location. Writing urls.py out to {urls_location}. Please "
                   "copy file to the proper location after script finishes.")
            self.stdout.write(self.style.WARNING(msg))
        with open(urls_location, "w+") as urls_file:
            urls_file.write(rendered)

        self.ok()

    def generate_secret_key(self) -> None:
        """Generates a new secret key."""
        self.status("  Generating secret key... ")
        self.context["SECRET_KEY"] = get_random_secret_key()
        self.ok()

    def handle(self, *args, **options) -> None:
        """Handles the setup process."""
        self.context["CREATE_DATE"] = timezone.now()
        self.context["PROJECT_NAME"] = settings.BASE_DIR.name
        self.context["HINTS_ENABLED"] = False
        self.welcome_banner()
        self.stdout.write(self.style.MIGRATE_HEADING("Initial setup:"))
        self.check_python()
        self.create_project_dirs(media_dir=options.get("media_dir"))
        self.generate_secret_key()
        self.get_target_type()
        # self.get_hint_preference()
        self.stdout.write(self.style.MIGRATE_HEADING("Copying templates:"))
        self.generate_config()
        self.generate_urls()
        self.run_migrations()
        self.create_pi()
        self.create_public_group()
        self.complete()

    def run_migrations(self) -> None:
        """Runs the initial database migrations."""
        self.status("  Running initial migrations... ")
        call_command("migrate", interactive=False, verbosity=0)
        self.ok()

    def create_project_dirs(self, media_dir) -> None:
        """Creates necessary project directories."""
        self.status("  Creating project directories... ")

        # Determine the base directory for the 'data' directory
        if media_dir:
            self.status("  Using custom path for media...")
            base_dir = Path(media_dir)
        else:
            base_dir = settings.BASE_DIR

        # Create a list of directories to be created
        directories = ["templates", "static", "tmp"]
        data_dir = base_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        self.context["MEDIA_ROOT"] = data_dir

        for dir_name in directories:
            dir_path = settings.BASE_DIR / dir_name
            dir_path.mkdir(exist_ok=True)

        # Create a ".keep" file in the "static" directory
        (settings.BASE_DIR / "static" / ".keep").touch(exist_ok=True)

        self.ok()

    def get_target_type(self) -> None:
        """Gets the target type for the project."""
        self.context["TARGET_TYPE"] = "SIDEREAL"

    def create_pi(self) -> None:
        """Creates a Principal Investigator (PI) superuser."""
        self.stdout.write(self.style.MIGRATE_HEADING("Principal Investigator (PI) and public user creation:"))
        call_command("createsuperuser", verbosity=0)
        self.status("  PI Superuser created... ")
        self.ok()

    def create_public_group(self) -> None:
        """Creates and configures the "Public" group."""
        self.status("  Setting up Public group... ")
        group = Group.objects.create(name="Public")
        group.user_set.add(*User.objects.all())
        group.save()
        self.ok()
