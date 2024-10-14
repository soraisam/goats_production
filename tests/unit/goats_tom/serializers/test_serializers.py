"""Test classes for serializers."""

from goats_tom.serializers import (
    DRAGONSFileFilterSerializer,
    DRAGONSFileSerializer,
    DRAGONSRecipeFilterSerializer,
    DRAGONSRecipeSerializer,
    DRAGONSReduceFilterSerializer,
    DRAGONSReduceSerializer,
    DRAGONSReduceUpdateSerializer,
    DRAGONSRunFilterSerializer,
    DRAGONSRunSerializer,
)
from goats_tom.tests.factories import (
    DRAGONSFileFactory,
    DRAGONSRecipeFactory,
    DRAGONSReduceFactory,
    DRAGONSRunFactory,
)
from django.forms.models import model_to_dict
from rest_framework.test import APITestCase


class TestDRAGONSFileSerializer(APITestCase):
    """Test class for `DRAGONSFileSerializer`."""

    def test_valid_data(self):
        """Test `DRAGONSFileSerializer` with valid data."""
        dragons_file = DRAGONSFileFactory()
        serializer = DRAGONSFileSerializer(dragons_file)

        self.assertEqual(
            serializer.data["product_id"], dragons_file.product_id,
        )
        

class TestDRAGONSFileFilterSerializer(APITestCase):
    """Test class for `DRAGONSFileFilterSerializer`."""

    def test_valid_data(self):
        """Test `DRAGONSFileFilterSerializer` with valid data."""
        valid_data = {
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

    def setUp(self):
        self.recipe = DRAGONSRecipeFactory()

    def test_valid_data(self):
        """Test `DRAGONSRecipeSerializer` with valid data."""
        serializer = DRAGONSRecipeSerializer(self.recipe)

        self.assertEqual(serializer.data["observation_type"], self.recipe.observation_type)
        self.assertEqual(serializer.data["name"], self.recipe.name)
        self.assertEqual(
            serializer.data["active_function_definition"], self.recipe.active_function_definition,
        )
        self.assertEqual(serializer.data["short_name"], self.recipe.short_name)

    def test_partial_update(self):
        """Test partial update of `DRAGONSRecipe`."""
        partial_data = {"function_definition": "Updated function definition", "uparms": "test"}
        serializer = DRAGONSRecipeSerializer(self.recipe, data=partial_data, partial=True)

        self.assertTrue(serializer.is_valid())
        updated_instance = serializer.save()
        self.assertEqual(
            updated_instance.active_function_definition, "Updated function definition",
        )
        self.assertEqual(
            updated_instance.function_definition, "Updated function definition",
        )
        self.assertEqual(
            updated_instance.uparms, "test",
        )

    def test_update_with_whitespace_only(self):
        """Test updating function definition with whitespace only to trigger reset."""
        data = {"function_definition": "   "}
        serializer = DRAGONSRecipeSerializer(self.recipe, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_instance = serializer.save()
        self.assertIsNone(updated_instance.function_definition)

    def test_function_definition_write_only(self):
        """Test that 'function_definition' is write-only and not included in the output.
        """
        serializer = DRAGONSRecipeSerializer(self.recipe)
        self.assertNotIn("function_definition", serializer.data)


class TestDRAGONSRecipeFilterSerializer(APITestCase):
    """Test class for `DRAGONSRecipeFilterSerializer`."""

    def test_valid_data(self):
        """Test `DRAGONSRecipeFilterSerializer` with valid data."""
        valid_data = {"dragons_run": 1, "observation_type": "BIAS", "include": ["help"]}
        serializer = DRAGONSRecipeFilterSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())


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
            serializer.data["config_filename"], dragons_run.config_filename,
        )
        self.assertEqual(
            serializer.data["output_directory"], dragons_run.output_directory,
        )
        self.assertEqual(
            serializer.data["cal_manager_filename"], dragons_run.cal_manager_filename,
        )
        self.assertEqual(serializer.data["log_filename"], dragons_run.log_filename)

    def test_invalid_data(self):
        """Test `DRAGONSRunSerializer` with invalid data."""
        invalid_data = {"output_directory": None}
        serializer = DRAGONSRunSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        
    def test_run_id_sanitization(self):
        """Test the sanitization of `run_id` with various edge cases."""
        
        test_cases = [
            ("NormalID2023", "normalid2023"),
            ("123_456-789", "123_456-789"),
            ("Test@ID#2023$", "testid2023"),
            ("Run ID with spaces", "run_id_with_spaces"),
            ("ID_with!special*chars", "id_withspecialchars"),
            ("ID-with.dots/and,commas", "id-withdotsandcommas")
        ]

        # Create a default instance with all necessary attributes set
        dragons_run = DRAGONSRunFactory()

        for input_id, expected in test_cases:
            with self.subTest(input_id=input_id):
                # Manually set the run_id for each test case
                dragons_run.run_id = input_id

                # Serialize to dictionary and modify the run_id
                dragons_run_data = model_to_dict(dragons_run)
                dragons_run_data['run_id'] = input_id  # Ensure run_id is updated for test

                serializer = DRAGONSRunSerializer(data=dragons_run_data)
                if serializer.is_valid():
                    self.assertEqual(serializer.validated_data['run_id'], expected)
                else:
                    self.fail(f"Serializer with run_id '{input_id}' should be valid but errors were: {serializer.errors}")


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


class TestDRAGONSReduceSerializer(APITestCase):
    """Test class for `DRAGONSReduceSerializer`."""

    def test_valid_data(self):
        """Test `DRAGONSReduceSerializer` with valid data."""
        recipe = DRAGONSRecipeFactory()
        valid_data = {"recipe_id": recipe.id}

        serializer = DRAGONSReduceSerializer(data=valid_data)
        self.assertTrue(
            serializer.is_valid(),
            msg=f"Serializer should be valid. Errors: {serializer.errors}",
        )

        reduction = serializer.save()
        self.assertIsNotNone(reduction.id, "Reduction should have an ID after saving.")
        self.assertEqual(
            reduction.recipe_id,
            recipe.id,
            "Reduction recipe ID should match the input.",
        )

    def test_invalid_data(self):
        """Test `DRAGONSReduceSerializer` with invalid data."""
        invalid_data = {"recipe_id": 999999}  # Assuming this ID does not exist

        serializer = DRAGONSReduceSerializer(data=invalid_data)
        self.assertFalse(
            serializer.is_valid(),
            "Serializer should not be valid with a non-existent recipe ID.",
        )
        self.assertIn(
            "recipe_id", serializer.errors, "Error key should be 'recipe_id'.",
        )


class TestDRAGONSReduceUpdateSerializer(APITestCase):
    """Test class for `DRAGONSReduceUpdateSerializer`."""

    def setUp(self):
        self.recipe = DRAGONSRecipeFactory()
        self.reduction = DRAGONSReduceFactory(recipe=self.recipe, status="running")

    def test_valid_update(self):
        """Test updating `DRAGONSReduce` with valid status change."""
        valid_data = {"status": "canceled"}
        serializer = DRAGONSReduceUpdateSerializer(self.reduction, data=valid_data)

        self.assertTrue(
            serializer.is_valid(),
            msg=f"Serializer should be valid. Errors: {serializer.errors}",
        )

        updated_reduction = serializer.save()
        self.assertEqual(
            updated_reduction.status,
            "canceled",
            "Reduction status should be updated to 'canceled'.",
        )
        self.assertTrue(
            updated_reduction.end_time is not None,
            "End time should be updated when canceled.",
        )

    def test_invalid_update_terminal_state(self):
        """Test updating `DRAGONSReduce` when it is already in a terminal state."""
        self.reduction.status = "done"
        self.reduction.save()
        invalid_data = {"status": "canceled"}
        serializer = DRAGONSReduceUpdateSerializer(self.reduction, data=invalid_data)

        self.assertFalse(
            serializer.is_valid(),
            "Serializer should not be valid when trying to update from a terminal state.",
        )
        self.assertIn(
            "status",
            serializer.errors,
            "Error message should include 'status' field when updating from a terminal state.",
        )

    def test_invalid_update_wrong_status(self):
        """Test updating `DRAGONSReduce` with an incorrect status value."""
        invalid_data = {
            "status": "running",
        }  # Assuming 'running' cannot be set directly
        serializer = DRAGONSReduceUpdateSerializer(self.reduction, data=invalid_data)

        self.assertFalse(
            serializer.is_valid(),
            "Serializer should not be valid when given an incorrect status value.",
        )
        self.assertIn(
            "status",
            serializer.errors,
            "Error message should include 'status' field for incorrect status value.",
        )


class TestDRAGONSReduceFilterSerializer(APITestCase):
    """Test class for `DRAGONSReduceFilterSerializer`."""

    def test_valid_data(self):
        """Test `DRAGONSReduceFilterSerializer` with valid data."""
        valid_data = {"status": ["running", "queued"], "not_finished": True, "run": 1}
        serializer = DRAGONSReduceFilterSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_status(self):
        """Test `DRAGONSReduceFilterSerializer` with invalid status."""
        invalid_data = {"status": ["invalid_status"], "not_finished": True, "run": 1}
        serializer = DRAGONSReduceFilterSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("status", serializer.errors)

    def test_invalid_not_finished(self):
        """Test `DRAGONSReduceFilterSerializer` with invalid not_finished."""
        invalid_data = {
            "status": ["running"],
            "not_finished": "invalid_boolean",
            "run": 1,
        }
        serializer = DRAGONSReduceFilterSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("not_finished", serializer.errors)

    def test_invalid_run(self):
        """Test `DRAGONSReduceFilterSerializer` with invalid run."""
        invalid_data = {
            "status": ["running"],
            "not_finished": True,
            "run": "invalid_integer",
        }
        serializer = DRAGONSReduceFilterSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("run", serializer.errors)

    def test_partial_valid_data(self):
        """Test `DRAGONSReduceFilterSerializer` with partial valid data."""
        valid_data = {"status": ["done"]}
        serializer = DRAGONSReduceFilterSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_empty_data(self):
        """Test `DRAGONSReduceFilterSerializer` with empty data."""
        valid_data = {}
        serializer = DRAGONSReduceFilterSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
