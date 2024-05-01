__all__ = ["DRAGONSFile"]


from django.db import models
from tom_dataproducts.models import DataProduct

from .dragons_run import DRAGONSRun


class DRAGONSFile(models.Model):
    dragons_run = models.ForeignKey(
        DRAGONSRun, on_delete=models.CASCADE, related_name="dragons_run_files"
    )
    data_product = models.ForeignKey(DataProduct, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("dragons_run", "data_product")

    def get_file_path(self) -> str:
        return self.data_product.data.path

    def get_file_type(self) -> str:
        return self.data_product.metadata.file_type
