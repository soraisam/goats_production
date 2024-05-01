"""Module that handles the DRAGONS run API."""

import re

from django.db.models import QuerySet
from gempy.utils.showrecipes import showprims
from recipe_system import cal_service
from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet
from tom_dataproducts.models import DataProduct

from goats_tom.models import DRAGONSFile, DRAGONSPrimitive, DRAGONSRecipe, DRAGONSRun
from goats_tom.serializers import DRAGONSRunFilterSerializer, DRAGONSRunSerializer


class DRAGONSRunsViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """A viewset that provides `create`, `retrieve`, `list`, and `delete` actions for a
    reduction run."""

    queryset = DRAGONSRun.objects.all()
    serializer_class = DRAGONSRunSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_serializer_class = DRAGONSRunFilterSerializer

    def get_queryset(self) -> QuerySet:
        """Retrieves the queryset filtered by different options.

        Returns
        -------
        QuerySet
            The filtered queryset.
        """
        queryset = super().get_queryset()

        # Run query parameters through the serializer.
        filter_serializer = self.filter_serializer_class(data=self.request.query_params)

        # Check if any filters provided.
        if filter_serializer.is_valid(raise_exception=False):
            observation_record_pk = filter_serializer.validated_data.get(
                "observation_record"
            )
            if observation_record_pk is not None:
                queryset = queryset.filter(observation_record__pk=observation_record_pk)

        return queryset

    def perform_create(self, serializer: DRAGONSRunSerializer) -> None:
        """Perform the creation of a `DRAGONSRun` instance using the provided
        serializer, initialize its directory, and link related DataProducts.

        Parameters
        ----------
        serializer : `DRAGONSRunSerializer`
            The serializer containing the validated data for creating a `DRAGONSRun`.
        """
        dragons_run = serializer.save()

        self.init_dragons_dir(dragons_run)

        # Link DataProducts for the run to enable/disable.
        data_products = DataProduct.objects.filter(
            observation_record=dragons_run.observation_record
        )
        for dp in data_products:
            DRAGONSFile.objects.update_or_create(
                dragons_run=dragons_run, data_product=dp, defaults={"enabled": True}
            )

        self.init_recipe_and_primitives(dragons_run)

    def init_dragons_dir(self, dragons_run: DRAGONSRun) -> None:
        """Initializes the output directory for a given DRAGONSRun instance.

        This method sets up the output directory, creates a calibration manager
        database, and writes the configuration file necessary for the run. The
        directory structure and files created are essential for the operation of
        DRAGONS data processing.

        Parameters
        ----------
        dragons_run : `DRAGONSRun`
            The `DRAGONSRun` instance for which the directory and necessary files are
            created.
        """
        # Create the output directory.
        output_dir = dragons_run.get_output_dir()
        output_dir.mkdir(parents=True)

        cal_manager_db_file = output_dir / "cal_manager.db"
        dragons_rc_file = output_dir / "dragonsrc"

        # Write the DRAGONS config file.
        with dragons_rc_file.open("w") as f:
            f.write(f"[calibs]\ndatabases = {cal_manager_db_file} get store")

        # Create the calibration manager for DRAGONS.
        cal_service.LocalDB(cal_manager_db_file, force_init=True)

    def init_recipe_and_primitives(self, dragons_run: DRAGONSRun) -> None:
        dragons_files = dragons_run.dragons_run_files.all()

        processed_file_types = set()

        for dragons_file in dragons_files:
            file_type = dragons_file.get_file_type()
            if file_type in processed_file_types:
                continue

            # Create a recipe and primitives for the default option for now.
            recipe_and_primitives = self.get_default_recipe_and_primitives(dragons_file)
            recipe = DRAGONSRecipe.objects.create(
                dragons_run=dragons_run,
                file_type=file_type,
                name=recipe_and_primitives["recipe"],
            )
            for primitive in recipe_and_primitives["primitives"]:
                DRAGONSPrimitive.objects.create(
                    recipe=recipe, name=primitive, is_enabled=True
                )

            # Don't add another recipe.
            processed_file_types.add(file_type)

    def get_default_recipe_and_primitives(self, dragons_file):
        output_text = showprims(dragons_file.get_file_path())

        return self.parse_showprims_output(output_text)

    def parse_showprims_output(self, output_text):
        # Regex to extract the "Input recipe:", "Matched recipe:" and the list of primitives
        recipe_pattern = r"Matched recipe:\s*(.+)"
        primitives_pattern = r"Primitives used:\s*((?:\s*p\.[^\n]+\n)+)"

        # Find matched recipe
        recipe_match = re.search(recipe_pattern, output_text)
        recipe = recipe_match.group(1).strip() if recipe_match else None

        # Find primitives list
        primitives_match = re.search(primitives_pattern, output_text)
        primitives_list = []
        if primitives_match:
            primitives_block = primitives_match.group(1).strip()
            # Split lines and strip the 'p.' prefix
            primitives_list = [
                line.strip()[2:].strip()
                for line in primitives_block.split("\n")
                if line.strip().startswith("p.")
            ]

        return {"recipe": recipe, "primitives": primitives_list}
