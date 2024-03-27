"""Model for file metadata for DRAGONS."""

__all__ = ["DRAGONSFileMetadata"]

from django.db import models

from .dragons_run import DRAGONSRun


class DRAGONSFileMetadata(models.Model):
    """Stores file metadata for a DRAGONS run.

    Attributes
    ----------
    dragons_run : `models.ForeignKey`
        The DRAGONS run this file list is associated with.
    file_type : `models.CharField`
        Type of the file (e.g., BIAS, DARK, FLAT, OBJECT, etc.).
    filename : `models.CharField`
        The name of the file.
    group_id : `models.CharField`
        Group identifier for the file, if applicable.
    exposure_time : `models.FloatField`
        Exposure time of the file.
    object_name : `models.CharField`
        Name of the observed object.
    central_wavelength : models.FloatField
        Central wavelength of the observation.
    wavelength_band : models.CharField
        Wavelength band of the observation.
    observation_date : models.DateField
        Date of the observation.
    roi_setting : models.CharField
        Region of interest setting of the detector.
    created : models.DateTimeField
        Time at which the file metadata was created.
    modified : models.DateTimeField
        Time at which the file metadata was last modified.
    enabled : `models.BooleanField`
        If the file is meant to be used in DRAGONS.
    archived : `models.BooleanField`
        If the file this metadata belongs to was deleted.
    """

    dragons_run = models.ForeignKey(
        DRAGONSRun, on_delete=models.CASCADE, related_name="files_metadata"
    )
    file_type = models.CharField(max_length=50)
    filename = models.CharField(max_length=255)
    group_id = models.CharField(max_length=255, null=True, blank=True)
    exposure_time = models.FloatField()
    object_name = models.CharField(max_length=255)
    central_wavelength = models.FloatField(null=True, blank=True)
    wavelength_band = models.CharField(max_length=50, null=True, blank=True)
    observation_date = models.DateField()
    roi_setting = models.CharField(max_length=50, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True)
    archived = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["dragons_run", "file_type"], name="file_type_idx"),
        ]
