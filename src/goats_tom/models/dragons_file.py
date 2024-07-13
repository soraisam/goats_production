__all__ = ["DRAGONSFile"]

import inspect
from typing import Any

from django.db import models
from gempy.scripts import showpars
from numpydoc.docscrape import NumpyDocString
from tom_dataproducts.models import DataProduct


class DRAGONSFile(models.Model):
    dragons_run = models.ForeignKey(
        "goats_tom.DRAGONSRun",
        on_delete=models.CASCADE,
        related_name="dragons_run_files",
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

    def list_primitives_and_docstrings(self) -> dict[str, Any]:
        """Lists all available primitives and their documentation for the file type
        associated with this DRAGONS file object.

        Returns
        -------
        `dict[str, Any]`
            A dictionary containing method names as keys and another dictionary as
            values, which includes parameters and their documentation, as well as the
            method's docstring parsed according to the numpy documentation standard.

        """
        data = {}
        primitive_obj, _ = showpars.get_pars(self.get_file_path())

        for item in dir(primitive_obj):
            if not item.startswith("_") and inspect.ismethod(
                getattr(primitive_obj, item),
            ):
                method = getattr(primitive_obj, item)
                params = primitive_obj.params[item]
                data[item] = {
                    "params": {
                        # Filter and store parameters that do not start with "debug".
                        k: {"value": v, "doc": params.doc(k)}
                        for k, v in params.items()
                        if not k.startswith("debug")
                    },
                    "docstring": {},
                }
                # Process the docstring.
                try:
                    docstring = NumpyDocString(method.__doc__)
                    # Parse and store the docstring content, transforming section titles
                    # to lowercase and replacing spaces with underscores.
                    data[item]["docstring"] = {
                        section.lower().replace(" ", "_"): content
                        for section, content in docstring._parsed_data.items()
                    }
                except (ValueError, TypeError):
                    # print(f"Error processing docstring for {item}: {str(e)}")
                    pass

        return data
