"""Module that handles the DRAGONS run API."""

import datetime
from datetime import timedelta

import astrodata
from django.db.models import Max, QuerySet
from django.http import HttpRequest
from recipe_system import cal_service
from rest_framework import mixins, permissions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from tom_dataproducts.models import DataProduct

from goats_tom.models import (
    BaseRecipe,
    DRAGONSFile,
    DRAGONSRecipe,
    DRAGONSRun,
    RecipesModule,
)
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

        # TODO: Use the new method for biases.
        # self._disable_old_biases(data_products, dragons_run)

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
        """This method processes each data product linked to the run, using its tags and
        instrument data to fetch applicable recipes and create or update corresponding
        `DRAGONSRecipe` instances. If a file matches the conditions (unprepared and not
        processed or is a BPM file), it initializes recipes, updates the database, and
        creates a DRAGONSFile record.

        Parameters
        ----------
        dragons_run : `DRAGONSRun`
            The DRAGONS run instance for which recipes are being initialized.

        """
        # TODO: Make this more intelligent.
        # Link DataProducts for the run to enable/disable.
        data_products = DataProduct.objects.filter(
            observation_record=dragons_run.observation_record,
        )

        for data_product in data_products:
            # Get the tags and instrument.
            ad = astrodata.open(data_product.data.path)
            tags = ad.tags
            instrument = ad.instrument(generic=True).lower()
            object_name = None
            # TODO: Is there a better place for this?
            descriptors = ad.descriptors

            # Skip if file is prepared or processed, unless it's a BPM file.
            if "BPM" not in tags and ("PREPARED" in tags or "PROCESSED" in tags):
                print("Skipping prepared or processed file.")
                continue

            # Get the file type and the object name if applicable.
            file_type = ad.observation_type().lower()
            if file_type == "object":
                object_name = ad.object()

            # if file_type not in processed_base_recipe_file_types:
            recipes_and_primitives = get_recipes_and_primitives(tags, instrument)

            # Create or update recipes in the database.
            for recipe_name, details in recipes_and_primitives["recipes"].items():
                recipes_module, created = RecipesModule.objects.get_or_create(
                    name=details["recipes_module"],
                    instrument=instrument,
                    version=dragons_run.version,
                )

                # Create or fetch the base recipe.
                base_recipe, base_recipe_created = BaseRecipe.objects.get_or_create(
                    name=recipe_name,
                    recipes_module=recipes_module,
                    defaults={
                        "function_definition": details["function_definition"],
                        "is_default": details["is_default"],
                    },
                )
                if base_recipe_created:
                    print(f"Created a BASE recipe: {recipe_name}")
                else:
                    print(f"Did not create a BASE recipe: {recipe_name}")

                # Create or get the recipe for this one.
                dragons_recipe, dragons_recipe_created = (
                    DRAGONSRecipe.objects.get_or_create(
                        dragons_run=dragons_run,
                        recipe=base_recipe,
                        object_name=object_name,
                        file_type=file_type,
                    )
                )

                if dragons_recipe_created:
                    print(f"Created a tmp recipe: {recipe_name}")
                else:
                    print(f"Did not create a tmp recipe: {recipe_name}")

            # Build the astrodata descriptors to save.
            astrodata_descriptors = {}
            for descriptor in descriptors:
                if hasattr(ad, descriptor):
                    try:
                        value = getattr(ad, descriptor)()
                        # Check for unsupported types and convert them.
                        if isinstance(value, (datetime.date, datetime.datetime)):
                            # Convert datetime or date to ISO formatted string.
                            value = value.isoformat()
                        elif not isinstance(value, (str, int, float, bool, type(None))):
                            # Convert any other unsupported types to string.
                            value = str(value)
                        astrodata_descriptors[descriptor] = value
                    except Exception as e:
                        print(f"Error accessing descriptor {descriptor}: {str(e)}")

            # Create a file for this run using the recipes module last retrieved.
            DRAGONSFile.objects.create(
                dragons_run=dragons_run,
                data_product=data_product,
                recipes_module=recipes_module,
                file_type=file_type,
                object_name=object_name,
                astrodata_descriptors=astrodata_descriptors,
                product_id=data_product.product_id,
                url=data_product.data.url,
            )

    def retrieve(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Retrieve a DRAGONS run instance along with optional included data based on
        query parameters.

        Parameters
        ----------
        request : `HttpRequest`
            The HTTP request object, containing query parameters.

        Returns
        -------
        `Response`
            Contains serialized DRAGONS run data with optional information.

        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Validate the query parameters.
        filter_serializer = self.filter_serializer_class(data=request.query_params)
        # If valid, attach the additional information.
        if filter_serializer.is_valid(raise_exception=False):
            include = filter_serializer.validated_data.get("include", [])

            if "groups" in include:
                data["groups"] = instance.list_groups()

        return Response(data)
