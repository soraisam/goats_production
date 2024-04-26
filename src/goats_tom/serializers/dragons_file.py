__all__ = ["DRAGONSFileSerializer", "DRAGONSFileFilterSerializer"]
from rest_framework import serializers

from goats_tom.models import DRAGONSFile


class DRAGONSFileSerializer(serializers.ModelSerializer):
    """Serializer for `DRAGONSFileSerializer` instances.

    Attributes
    ----------
    product_id : `serializers.CharField`
        The unique identifier of the data product.
    observation_id : `serializers.CharField`
        The observation ID associated with the data product.
    file_type : `serializers.CharField`
        The type of file, e.g., BIAS, DARK, FLAT.
    group_id : `serializers.CharField`
        An optional group ID for grouping related data products.
    exposure_time : `serializers.FloatField`
        The exposure time of the data product.
    object_name : `serializers.CharField`
        The name of the observed object.
    central_wavelength : `serializers.FloatField`
        The central wavelength of the observation.
    wavelength_band : `serializers.CharField`
        The wavelength band of the observation.
    observation_date : `serializers.DateField`
        The date when the observation was made.
    roi_setting : `serializers.CharField`
        The region of interest setting of the detector.
    enabled : `serializers.BooleanField`
        Indicates whether the data product is enabled for processing in a DRAGONS run.

    Notes
    -----
    This serializer dynamically maps `DataProduct` and `DataProductMetadata`
    fields to a flattened structure.
    """

    product_id = serializers.CharField(source="data_product.product_id")
    observation_id = serializers.CharField(
        source="data_product.observation_record.observation_id"
    )
    file_type = serializers.CharField(source="data_product.metadata.file_type")
    group_id = serializers.CharField(
        source="data_product.metadata.group_id", allow_null=True
    )
    exposure_time = serializers.FloatField(
        source="data_product.metadata.exposure_time", allow_null=True
    )
    object_name = serializers.CharField(
        source="data_product.metadata.object_name", allow_null=True
    )
    central_wavelength = serializers.FloatField(
        source="data_product.metadata.central_wavelength", allow_null=True
    )
    wavelength_band = serializers.CharField(
        source="data_product.metadata.wavelength_band", allow_null=True
    )
    observation_date = serializers.DateField(
        source="data_product.metadata.observation_date", allow_null=True
    )
    roi_setting = serializers.CharField(
        source="data_product.metadata.roi_setting", allow_null=True
    )
    enabled = serializers.BooleanField()

    class Meta:
        model = DRAGONSFile
        fields = [
            "dragons_run",
            "product_id",
            "observation_id",
            "file_type",
            "group_id",
            "exposure_time",
            "object_name",
            "central_wavelength",
            "wavelength_band",
            "observation_date",
            "roi_setting",
            "enabled",
        ]

    def update(self, instance, validated_data):
        instance.enabled = validated_data.get("enabled", instance.enabled)
        instance.save()
        return instance


class DRAGONSFileFilterSerializer(serializers.Serializer):
    group_by_file_type = serializers.BooleanField(required=False, default=False)
    dragons_run = serializers.IntegerField(required=False)
