"""Test classes for serializers."""

from goats_tom.serializers import (
    DRAGONSFileFilterSerializer,
    DRAGONSFileSerializer,
    DRAGONSRecipeFilterSerializer,
    DRAGONSRecipeSerializer,
    DRAGONSRunFilterSerializer,
    DRAGONSRunSerializer,
)
from goats_tom.tests.factories import (
    DRAGONSFileFactory,
    DRAGONSRecipeFactory,
    DRAGONSRunFactory,
)
from rest_framework.test import APITestCase


class TestDRAGONSFileSerializer(APITestCase):
    """Test class for `DRAGONSFileSerializer`."""

    def test_valid_data(self):
        """Test `DRAGONSFileSerializer` with valid data."""
        dragons_file = DRAGONSFileFactory()
        serializer = DRAGONSFileSerializer(dragons_file)

        self.assertEqual(
            serializer.data["product_id"], dragons_file.data_product.product_id
        )
        self.assertEqual(
            serializer.data["file_type"], dragons_file.data_product.metadata.file_type
        )

    def test_invalid_data(self):
        """Test `DRAGONSFileSerializer` with invalid data."""
        invalid_data = {
            "enabled": None  # Invalid as enabled should not be None
        }
        serializer = DRAGONSFileSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    def test_partial_update(self):
        """Test partial update of `DRAGONSFile`."""
        dragons_file = DRAGONSFileFactory(enabled=True)
        partial_data = {"enabled": False}
        serializer = DRAGONSFileSerializer(
            dragons_file, data=partial_data, partial=True
        )

        self.assertTrue(serializer.is_valid())
        updated_instance = serializer.save()
        self.assertEqual(updated_instance.enabled, False)

    def test_partial_update_invalid_data(self):
        """Test partial update of `DRAGONSFile`."""
        dragons_file = DRAGONSFileFactory()
        original_product_id = dragons_file.data_product.product_id
        original_observation_id = (
            dragons_file.data_product.observation_record.observation_id
        )
        original_url = dragons_file.data_product.data.url

        update_data = {
            "product_id": "new-product-id",
            "observation_id": "new-observation-id",
            "url": "new-url",
            "enabled": not dragons_file.enabled,
        }

        serializer = DRAGONSFileSerializer(dragons_file, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_instance = serializer.save()

        # Check that immutable fields have not changed.
        self.assertEqual(updated_instance.data_product.product_id, original_product_id)
        self.assertEqual(
            updated_instance.data_product.observation_record.observation_id,
            original_observation_id,
        )
        self.assertEqual(updated_instance.data_product.data.url, original_url)
        # Check that the 'enabled' field has been updated.
        self.assertEqual(updated_instance.enabled, update_data["enabled"])


class TestDRAGONSFileFilterSerializer(APITestCase):
    """Test class for `DRAGONSFileFilterSerializer`."""

    def test_valid_data(self):
        """Test `DRAGONSFileFilterSerializer` with valid data."""
        valid_data = {
            "group_by_file_type": True,
            "dragons_run": 1,
            "include": ["header"],
        }
        serializer = DRAGONSFileFilterSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_data(self):
        """Test `DRAGONSFileFilterSerializer` with invalid data."""
        invalid_data = {"include": ["invalid_option"]}
        serializer = DRAGONSFileFilterSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())


class TestDRAGONSRecipeSerializer(APITestCase):
    """Test class for `DRAGONSRecipeSerializer`."""

    def test_valid_data(self):
        """Test `DRAGONSRecipeSerializer` with valid data."""
        recipe = DRAGONSRecipeFactory()
        serializer = DRAGONSRecipeSerializer(recipe)

        self.assertEqual(serializer.data["file_type"], recipe.file_type)
        self.assertEqual(serializer.data["name"], recipe.name)
        self.assertEqual(
            serializer.data["function_definition"], recipe.function_definition
        )
        self.assertEqual(serializer.data["short_name"], recipe.short_name)

    def test_invalid_data(self):
        """Test `DRAGONSRecipeSerializer` with invalid data."""
        invalid_data = {
            "file_type": "",
            "name": "",
            "function_definition": "Valid Function Definition",
            "dragons_run": None,
        }
        serializer = DRAGONSRecipeSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("file_type", serializer.errors)
        self.assertIn("name", serializer.errors)
        self.assertIn("dragons_run", serializer.errors)

    def test_partial_update(self):
        """Test partial update of `DRAGONSRecipe`."""
        recipe = DRAGONSRecipeFactory()
        partial_data = {"function_definition": "Updated function definition"}
        serializer = DRAGONSRecipeSerializer(recipe, data=partial_data, partial=True)

        self.assertTrue(serializer.is_valid())
        updated_instance = serializer.save()
        self.assertEqual(
            updated_instance.function_definition, "Updated function definition"
        )


class TestDRAGONSRecipeFilterSerializer(APITestCase):
    """Test class for `DRAGONSRecipeFilterSerializer`."""

    def test_valid_data(self):
        """Test `DRAGONSRecipeFilterSerializer` with valid data."""
        valid_data = {"dragons_run": 1, "file_type": "BIAS"}
        serializer = DRAGONSRecipeFilterSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_data(self):
        """Test `DRAGONSRecipeFilterSerializer` with invalid data."""
        # TODO: This should be testing the options for file_type.
        pass


class TestDRAGONSRunSerializer(APITestCase):
    """Test class for `DRAGONSRunSerializer`."""

    def test_valid_data(self):
        """Test `DRAGONSRunSerializer` with valid data."""
        dragons_run = DRAGONSRunFactory()
        serializer = DRAGONSRunSerializer(dragons_run)

        self.assertEqual(
            serializer.data["observation_id"],
            dragons_run.observation_record.observation_id,
        )
        self.assertEqual(serializer.data["run_id"], dragons_run.run_id)
        self.assertEqual(
            serializer.data["config_filename"], dragons_run.config_filename
        )
        self.assertEqual(
            serializer.data["output_directory"], dragons_run.output_directory
        )
        self.assertEqual(
            serializer.data["cal_manager_filename"], dragons_run.cal_manager_filename
        )
        self.assertEqual(serializer.data["log_filename"], dragons_run.log_filename)

    def test_invalid_data(self):
        """Test `DRAGONSRunSerializer` with invalid data."""
        invalid_data = {"output_directory": None}
        serializer = DRAGONSRunSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())


class TestDRAGONSRunFilterSerializer(APITestCase):
    """Test class for `DRAGONSRunFilterSerializer`."""

    def test_valid_data(self):
        """Test `DRAGONSRunFilterSerializer` with valid data."""
        valid_data = {"observation_record": 1}
        serializer = DRAGONSRunFilterSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_data(self):
        """Test `DRAGONSRunSerializer` with invalid data."""
        invalid_data = {
            "config_filename": "",
            "output_directory": "",
            "cal_manager_filename": "",
            "log_filename": "",
        }
        serializer = DRAGONSRunSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("config_filename", serializer.errors)
        self.assertIn("cal_manager_filename", serializer.errors)
