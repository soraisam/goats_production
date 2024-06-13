"""Model for DRAGONS runs."""

__all__ = ["DRAGONSRun"]

from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.db import models
from tom_observations.models import ObservationRecord


class DRAGONSRun(models.Model):
    """
    Represents a DRAGONS run setup configuration.

    This model stores configuration data for a DRAGONS run, including
    references to the associated observation record, run identifier,
    configuration filename, output directory, calibration manager filename,
    and log filename.

    Attributes
    ----------
    observation_record : `models.ForeignKey`
        The ObservationRecord this DRAGONS run is associated with.
    run_id : `models.CharField`
        Unique ID for the DRAGONS run, with a default format including
        timestamp.
    config_filename : `models.CharField`
        Filename for the DRAGONS configuration, not editable post-creation.
    output_directory : `models.CharField`
        Directory for output files from the DRAGONS run.
    cal_manager_filename : `models.CharField`
        Filename for the DRAGONS calibration manager, not editable
        post-creation.
    log_filename : `models.CharField`
        Filename for the DRAGONS run log, read-only.
    created : `models.DateTimeField`
        The time at which this object was created.
    modified : `models.DateTimeField`
        The time at which this object was last modified.

    Methods
    -------
    save(*args, **kwargs) -> None:
        Saves the DRAGONSRun instance, applying default values for `run_id` and
        `output_directory` if not provided.

    get_output_dir() -> Path:
        Constructs and returns the full path to the output directory.

    get_raw_dir() -> Path:
        Constructs and returns the full path to the raw directory based on the
        observation record's properties.
    """

    observation_record = models.ForeignKey(
        ObservationRecord, on_delete=models.CASCADE, related_name="dragons_runs"
    )
    run_id = models.CharField(
        max_length=255,
        blank=True,
    )
    config_filename = models.CharField(max_length=30, default="dragonsrc")
    output_directory = models.CharField(
        max_length=255,
        blank=True,
    )
    cal_manager_filename = models.CharField(max_length=30, default="cal_manager.db")
    log_filename = models.CharField(max_length=30, default="log.log", editable=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensure run_id is unique within the scope of each
        # "observation_record".
        constraints = [
            models.UniqueConstraint(
                fields=["observation_record", "run_id"],
                name="unique_observation_run_id",
            )
        ]
        # Index by "run_id" for easy filtering and getting.
        indexes = [
            models.Index(fields=["run_id"], name="run_id_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.observation_record.observation_id}.{self.run_id}"

    def save(self, *args, **kwargs) -> None:
        """Saves the DRAGONSRun instance.

        Applies default values for "run_id" and "output_directory" if they are
        not provided.
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        if not self.run_id:
            self.run_id = f"run-{timestamp}"
        if not self.output_directory:
            self.output_directory = f"reduced-{timestamp}"

        return super(DRAGONSRun, self).save(*args, **kwargs)

    def get_output_dir(self) -> Path:
        """Returns the full path to the output directory.

        Returns
        -------
        `Path`
            The full path to the output directory.
        """
        return self.get_raw_dir() / self.output_directory

    def get_cal_manager_db_file(self) -> Path:
        """Returns the full path to the calibration manager database file.

        Returns
        -------
        `Path`
            The full path to the calibration manager database file.
        """
        return self.get_output_dir() / self.cal_manager_filename

    def get_log_file(self) -> Path:
        """Returns the full path to the log file.

        Returns
        -------
        `Path`
            The full path to the log file.
        """
        return self.get_output_dir() / self.log_filename

    def get_config_file(self) -> Path:
        """Returns the full path to the configuration file.

        Returns
        -------
        `Path`
            The full path to the configuration file.
        """
        return self.get_output_dir() / self.config_filename

    def get_raw_dir(self) -> Path:
        """
        Returns the full path to the raw directory.

        Returns
        -------
        `Path`
            The full path to the associated observation ID directory.
        """

        return (
            settings.MEDIA_ROOT
            / self.observation_record.target.name
            / self.observation_record.facility
            / self.observation_record.observation_id
        )
