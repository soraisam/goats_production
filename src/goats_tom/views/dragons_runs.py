"""Module that handles the DRAGONS run API."""

import re
from datetime import timedelta

from django.db.models import Max, QuerySet
from gempy.utils.showrecipes import showprims
from recipe_system import cal_service
from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet
from tom_dataproducts.models import DataProduct

from goats_tom.models import DRAGONSFile, DRAGONSRecipe, DRAGONSRun
from goats_tom.serializers import DRAGONSRunFilterSerializer, DRAGONSRunSerializer
from goats_tom.utils import get_short_name


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

        self._init_dragons_dir(dragons_run)

        # Link DataProducts for the run to enable/disable.
        data_products = DataProduct.objects.filter(
            observation_record=dragons_run.observation_record
        ).select_related("metadata")

        DRAGONSFile.objects.bulk_create(
            [
                DRAGONSFile(dragons_run=dragons_run, data_product=dp, enabled=True)
                for dp in data_products
            ],
            ignore_conflicts=True,
        )

        self._disable_old_biases(data_products, dragons_run)

        self._init_recipe_and_primitives(dragons_run)

    def _disable_old_biases(
        self, data_products: QuerySet, dragons_run: DRAGONSRun, days: float | None = 10
    ) -> None:
        """Disables bias `DRAGONSFiles` outside of a defined window around the latest
        object observation date.

        Parameters
        ----------
        data_products : `QuerySet`
            A queryset of `DataProduct` instances linked to a specific `DRAGONSRun`.
        dragons_run : `DRAGONSRun`
            The `DRAGONSRun` instance for which bias files will be evaluated and
            potentially disabled.
        days : `float`, optional
            The number of days before and after the latest object observation date to
            consider; defaults to 10.
        """
        # Determine the latest observation date for 'object' file types.
        latest_object_date = data_products.filter(
            metadata__file_type="object"
        ).aggregate(Max("metadata__observation_date"))[
            "metadata__observation_date__max"
        ]

        if latest_object_date:
            # Calculate the start and end of the 10-day window.
            start_date = latest_object_date - timedelta(days=days)
            end_date = latest_object_date + timedelta(days=days)

            # Disable bias files outside the window.
            bias_products_to_disable = data_products.filter(
                metadata__file_type="BIAS"
            ).exclude(
                metadata__observation_date__range=(start_date, end_date),
            )

            # Update the enabled status for BIAS files outside the window.
            DRAGONSFile.objects.filter(
                dragons_run=dragons_run, data_product__in=bias_products_to_disable
            ).update(enabled=False)

    def _init_dragons_dir(self, dragons_run: DRAGONSRun) -> None:
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

        cal_manager_db_file = dragons_run.get_cal_manager_db_file()
        config_file = dragons_run.get_config_file()

        # Write the DRAGONS config file.
        with config_file.open("w") as f:
            f.write(f"[calibs]\ndatabases = {cal_manager_db_file} get store")

        # Create the calibration manager for DRAGONS.
        cal_service.LocalDB(cal_manager_db_file, force_init=True)

    def _init_recipe_and_primitives(self, dragons_run: DRAGONSRun) -> None:
        dragons_files = dragons_run.dragons_run_files.all()

        processed_file_types = set()

        for dragons_file in dragons_files:
            file_type = dragons_file.get_file_type()
            if file_type in processed_file_types:
                continue

            # Create a recipe and primitives for the default option for now.
            recipe, function_definition = self.get_default_recipe_and_primitives(
                dragons_file
            )
            recipe = DRAGONSRecipe.objects.create(
                dragons_run=dragons_run,
                file_type=file_type,
                name=recipe,
                function_definition=function_definition,
            )

            # Don't add another recipe.
            processed_file_types.add(file_type)

    def get_default_recipe_and_primitives(self, dragons_file):
        output_text = showprims(dragons_file.get_file_path())

        return self.parse_showprims_output(output_text)

    def parse_showprims_output(self, output_text) -> tuple[str, str]:
        # Regex to extract the "Matched recipe:" and the list of primitives as a
        # function.
        recipe_pattern = r"Matched recipe:\s*(.+)"

        # Find matched recipe
        recipe_match = re.search(recipe_pattern, output_text)
        recipe = recipe_match.group(1).strip() if recipe_match else None
        func_name = get_short_name(recipe)

        # Regex to extract the list of primitives as a function.
        primitives_pattern = r"Primitives used:\s*((?:\s*p\.[^\n]+\n)+)"
        primitives_match = re.search(primitives_pattern, output_text)
        primitives_list = (
            primitives_match.group(1).strip().split("\n") if primitives_match else []
        )

        # Format the function definition.
        function_definition = f"def {func_name}(p):\n"
        for primitive in primitives_list:
            function_definition += f"    {primitive.strip()}\n"
        return recipe, function_definition
