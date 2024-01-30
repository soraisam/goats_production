# test_models.py
import pytest
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from goats_tom.tests.factories import (
    DataProductFactory,
    GOALoginFactory,
    ProgramKeyFactory,
    ReducedDatumFactory,
    TaskProgressFactory,
    UserKeyFactory,
)


@pytest.mark.django_db
def test_goalogin_set_password():
    """Test to verify that the set_password method correctly hashes the
    password.
    """
    # Create a GOALogin instance with a factory
    goa_login = GOALoginFactory(password="testpassword")

    # Check if the password is correctly hashed
    assert "testpassword", goa_login.password


@pytest.mark.django_db
def test_task_progress_factory():
    # Test the TaskProgress factory.
    task = TaskProgressFactory.create()

    assert task.task_id is not None
    assert 0 <= task.progress < 100
    assert task.status == "running"
    assert not task.done
    assert task.start_time <= timezone.now()
    assert task.end_time is None
    assert task.error_message is None
    assert task.user is not None

    # Test the finish method.
    task.finish(error_message="Test error")
    assert task.status == "failed"
    assert task.error_message == "Test error"
    assert task.progress == 100
    task.done = True
    assert task.total_time != "N/A"


@pytest.mark.django_db
class TestDataProductFactory:
    def test_create_dataproduct(self):
        # Test creating a simple DataProduct without any overrides.
        data_product = DataProductFactory()
        assert data_product.pk is not None

    def test_dataproduct_with_overrides(self):
        # Test creating a DataProduct with some field overrides.
        custom_product_id = "custom_id"
        data_product = DataProductFactory(product_id=custom_product_id)
        assert data_product.product_id == custom_product_id

    def test_dataproduct_validation(self):
        # Test that creating a DataProduct with invalid data raises a
        # ValidationError.
        with pytest.raises(ValidationError):
            invalid_data_product = DataProductFactory(data_product_type="invalid_type")
            invalid_data_product.full_clean()


@pytest.mark.django_db
class TestReducedDatumFactory:
    def test_create_reduceddatum(self):
        # Test creating a simple ReducedDatum without any overrides.
        reduced_datum = ReducedDatumFactory()
        assert reduced_datum.pk is not None

    def test_reduceddatum_with_overrides(self):
        # Test creating a ReducedDatum with some field overrides.
        custom_value = {"magnitude": 20.0, "filter": "g", "error": 0.01}
        reduced_datum = ReducedDatumFactory(value=custom_value)
        assert reduced_datum.value == custom_value

    def test_reduceddatum_validation(self):
        # Test that creating a ReducedDatum with invalid data raises a
        # ValidationError.
        with pytest.raises(ValidationError):
            invalid_reduced_datum = ReducedDatumFactory(data_type="invalid_type")
            invalid_reduced_datum.full_clean()


@pytest.mark.django_db
class KeyFactoryTest(TestCase):
    def test_user_key_factory(self):
        user_key = UserKeyFactory()
        self.assertIsNotNone(user_key.id)
        self.assertTrue(user_key.email.endswith("@example.com"))
        self.assertIn(user_key.site, ["GS", "GN"])
        self.assertFalse(user_key.is_active)

    def test_program_key_factory(self):
        program_key = ProgramKeyFactory()
        self.assertIsNotNone(program_key.id)
        self.assertTrue(program_key.program_id.startswith("GN-2024A-Q-"))
        self.assertIn(program_key.site, ["GS", "GN"])
