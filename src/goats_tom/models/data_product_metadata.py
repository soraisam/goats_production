"""Model for file metadata for a data product."""

__all__ = ["DataProductMetadata"]

from django.db import models
from tom_dataproducts.models import DataProduct


def default_observation_subtypes() -> list:
    return []


class DataProductMetadata(models.Model):
    """Represents metadata associated with a data product.

    Attributes
    ----------
    data_product : `models.OneToOneField`
        The data product this metadata is associated with.
    file_type : `models.CharField`
        Type of the file (e.g., BIAS, DARK, FLAT).
    observation_subtypes : `models.JSONField`
        The subtypes of the file (e.g., filter).
    group_id : `models.CharField`
        Group identifier for the file, if applicable.
    exposure_time : `models.FloatField`
        Exposure time of the file.
    object_name : `models.CharField`
        Name of the observed object.
    central_wavelength : `models.FloatField`
        Central wavelength of the observation.
    wavelength_band : `models.CharField`
        Wavelength band of the observation.
    observation_date : `models.DateField`
        Date of the observation.
    roi_setting : `models.CharField`
        Region of interest setting of the detector.

    """

    data_product = models.OneToOneField(
        DataProduct,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="metadata",
    )
    file_type = models.CharField(max_length=50, null=True, blank=True)
    # observation_subtypes = models.JSONField(
    #     blank=True,
    #     help_text="Field for storing subtypes of the observation.",
    #     default=default_observation_subtypes,
    # )
    group_id = models.CharField(max_length=255, null=True, blank=True)
    exposure_time = models.FloatField(null=True, blank=True)
    object_name = models.CharField(max_length=255, null=True, blank=True)
    central_wavelength = models.FloatField(null=True, blank=True)
    wavelength_band = models.CharField(max_length=50, null=True, blank=True)
    observation_date = models.DateField(null=True, blank=True)
    roi_setting = models.CharField(max_length=50, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)
    tags = models.JSONField(editable=False)
    instrument = models.CharField(max_length=50, editable=False, blank=True, null=True)

    def __str__(self):
        return f"Metadata for {self.data_product.product_id}"
