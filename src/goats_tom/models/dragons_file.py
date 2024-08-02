"""Module for `DRAGONSFile` model."""

__all__ = ["DRAGONSFile"]

import inspect
from typing import Any

from django.db import models
from gempy.scripts import showpars
from numpydoc.docscrape import NumpyDocString
from tom_dataproducts.models import DataProduct


class DRAGONSFile(models.Model):
    """Represents a file associated with a DRAGONS run.

    Attributes
    ----------
    dragons_run : `models.ForeignKey`
        A foreign key linking to the `DRAGONSRun` instance.
    data_product : `models.ForeignKey`
        A foreign key to the `DataProduct` model that details the data
        product associated with this file.
    enabled : `models.BooleanField`
        A boolean flag indicating whether the file is active and should be
        considered in operations and processes.
    modified : `models.DateTimeField`
        The date and time the file was last modified, automatically set to
        the current timestamp when the file object is updated.
    recipes_module : `models.ForeignKey`
        An optional foreign key to the `RecipesModule`, indicating which
        recipes module is associated with this file.
    file_type : `models.CharField`
        A character field storing the type of the file.
    object_name : `models.CharField`
        An optional character field storing the name of the object related to
        the file, if applicable.

    """

    dragons_run = models.ForeignKey(
        "goats_tom.DRAGONSRun",
        on_delete=models.CASCADE,
        related_name="dragons_run_files",
    )
    data_product = models.ForeignKey(DataProduct, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    modified = models.DateTimeField(auto_now=True)
    recipes_module = models.ForeignKey(
        "goats_tom.RecipesModule",
        on_delete=models.CASCADE,
        null=True,
        related_name="files",
    )
    file_type = models.CharField(max_length=50, null=True, blank=True)
    object_name = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ("dragons_run", "data_product")

    @property
    def file_path(self) -> str:
        """Gets the file path from the data product.

        Returns
        -------
        `str`
            The file path.
        """
        return self.data_product.data.path

    @property
    def product_id(self) -> str:
        """Returns the product ID for the file.

        Returns
        -------
        `str`
            The product ID.
        """
        return self.data_product.product_id

    @property
    def observation_id(self) -> str:
        """Returns the observation ID for the file.

        Returns
        -------
        `str`
            The observation ID.
        """
        return self.data_product.observation_record.observation_id

    @property
    def url(self) -> str:
        """Returns the URL to download the file.

        Returns
        -------
        `str`
            The download URL.
        """
        return self.data_product.data.url

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
        primitive_obj, _ = showpars.get_pars(self.file_path)

        for item in dir(primitive_obj):
            if not item.startswith("_") and inspect.ismethod(
                getattr(primitive_obj, item),
            ):
                method = getattr(primitive_obj, item)
                params = primitive_obj.params[item]
                data[item] = {
                    "params": {
                        # Filter and store parameters that do not start with "debug".
                        k: {"value": f"{v}", "doc": f"{params.doc(k)}"}
                        for k, v in params.items()
                        if not k.startswith("debug")
                    },
                    "docstring": {},
                }
                try:
                    docstring = NumpyDocString(method.__doc__)
                    # Parse and store the docstring content, transforming section titles
                    # to lowercase and replacing spaces with underscores.
                    data[item]["docstring"] = {
                        section.lower().replace(" ", "_"): content
                        for section, content in docstring._parsed_data.items()
                    }
                except (ValueError, TypeError) as e:
                    print(f"Error processing docstring for {item}: {str(e)}")
                    pass

        return data
