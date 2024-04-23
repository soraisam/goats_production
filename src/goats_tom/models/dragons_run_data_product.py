__all__ = ["DRAGONSRunDataProduct"]

from django.db import models
from tom_dataproducts.models import DataProduct

from .dragons_run import DRAGONSRun


class DRAGONSRunDataProduct(models.Model):
    dragons_run = models.ForeignKey(
        DRAGONSRun, on_delete=models.CASCADE, related_name="run_data_products"
    )
    data_product = models.ForeignKey(DataProduct, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("dragons_run", "data_product")
