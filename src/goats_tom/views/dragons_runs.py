"""Module that handles the DRAGONS run API."""

from django.db.models import QuerySet
from recipe_system import cal_service
from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet
from tom_dataproducts.models import DataProduct

from goats_tom.models import DRAGONSFile, DRAGONSRun
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

        # run query parameters through the serializer.
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
