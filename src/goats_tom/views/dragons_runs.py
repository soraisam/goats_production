"""Module that handles the DRAGONS run API."""

from datetime import timedelta

from django.db.models import Max, QuerySet
from recipe_system import cal_service
from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet
from tom_dataproducts.models import DataProduct

from goats_tom.models import BaseRecipe, DRAGONSFile, DRAGONSRecipe, DRAGONSRun
from goats_tom.serializers import DRAGONSRunFilterSerializer, DRAGONSRunSerializer
from goats_tom.utils import get_recipes_and_primitives


class DRAGONSRunsViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """A viewset that provides `create`, `retrieve`, `list`, and `delete` actions for a
    reduction run.
    """

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
                "observation_record",
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
            observation_record=dragons_run.observation_record,
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
        self,
        data_products: QuerySet,
        dragons_run: DRAGONSRun,
        days: float | None = 10,
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
            metadata__file_type="object",
        ).aggregate(Max("metadata__observation_date"))[
            "metadata__observation_date__max"
        ]

        if latest_object_date:
            # Calculate the start and end of the 10-day window.
            start_date = latest_object_date - timedelta(days=days)
            end_date = latest_object_date + timedelta(days=days)

            # Disable bias files outside the window.
            bias_products_to_disable = data_products.filter(
                metadata__file_type="BIAS",
            ).exclude(
                metadata__observation_date__range=(start_date, end_date),
            )

            # Update the enabled status for BIAS files outside the window.
            DRAGONSFile.objects.filter(
                dragons_run=dragons_run,
                data_product__in=bias_products_to_disable,
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
        """Initializes recipes and their primitives for a DRAGONS run based on the file
        types available in the run. This method creates new recipe if they do not
        already exist for the file type and version and creates corresponding
        `DRAGONSRecipe` instances.

        Parameters
        ----------
        dragons_run : `DRAGONSRun`
            The DRAGONS run instance for which recipes are being initialized.

        """
        dragons_files = dragons_run.dragons_run_files.all()
        version = dragons_run.version
        existing_recipes = BaseRecipe.objects.filter(version=version)

        processed_base_recipe_file_types = {
            recipe.file_type for recipe in existing_recipes
        }
        processed_recipe_file_types = set()

        for dragons_file in dragons_files:
            file_type = dragons_file.get_file_type()

            if file_type not in processed_base_recipe_file_types:
                recipes_and_primitives = get_recipes_and_primitives(
                    dragons_file.get_file_path(),
                )

                # Create or update recipes in the database.
                for recipe_name, details in recipes_and_primitives["recipes"].items():
                    BaseRecipe.objects.update_or_create(
                        file_type=file_type,
                        name=recipe_name,
                        version=version,
                        function_definition=details["function_definition"],
                        is_default=details["is_default"],
                    )

                # Mark this file_type as processed to avoid duplicate processing
                processed_base_recipe_file_types.add(file_type)

            if file_type not in processed_recipe_file_types:
                # Fetch all existing base recipes for this file type and version
                existing_recipes_for_file_type = BaseRecipe.objects.filter(
                    file_type=file_type,
                    version=version,
                )
                for existing_recipe in existing_recipes_for_file_type:
                    # Create the recipe linking the base recipe.
                    DRAGONSRecipe.objects.create(
                        dragons_run=dragons_run,
                        recipe=existing_recipe,
                    )
                # Add to the file types to skip next time.
                processed_recipe_file_types.add(file_type)
