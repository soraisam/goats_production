from datetime import timedelta

import pytest
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from django.utils.crypto import get_random_string
from goats_tom.tests.factories import (
    GOALoginFactory,
    ProgramKeyFactory,
    TaskProgressFactory,
    UserFactory,
    UserKeyFactory,
)


@pytest.mark.django_db
class TestGOALoginModel(TestCase):
    def setUp(self):
        self.goa_login = GOALoginFactory()

    def test_empty_password(self):
        self.goa_login.password = ""
        with pytest.raises(ValidationError):
            self.goa_login.clean()

    def test_long_password(self):
        long_password = get_random_string(1000)
        self.goa_login.set_password(long_password)
        self.goa_login.save()
        assert check_password(long_password, self.goa_login.password)

    def test_special_characters_in_password(self):
        special_password = "!@#$%^&*()_+|"
        self.goa_login.set_password(special_password)
        self.goa_login.save()
        assert check_password(special_password, self.goa_login.password)


@pytest.mark.django_db
class TestTaskProgressModel(TestCase):
    def setUp(self):
        self.task = TaskProgressFactory()

    def test_negative_progress(self):
        self.task.progress = -10
        with pytest.raises(ValidationError):
            self.task.full_clean()

    def test_progress_over_100(self):
        self.task.progress = 110
        with pytest.raises(ValidationError):
            self.task.full_clean()

    def test_immediate_task_completion(self):
        self.task.finish()
        self.task.finalize()
        assert self.task.total_time == "0s"

    def test_long_duration_task(self):
        self.task.start_time = timezone.now() - timedelta(
            days=1
        )  # Simulate a long-running task
        self.task.finish()
        self.task.finalize()
        assert "1d" in self.task.total_time


@pytest.mark.django_db
class TestKeyModels:
    def test_key_activation(self):
        # Test activating a key.
        user_key = UserKeyFactory()
        assert not user_key.is_active
        user_key.activate()
        assert user_key.is_active

    def test_key_deactivation(self):
        # Test deactivating a key.
        user_key = UserKeyFactory(is_active=True)
        assert user_key.is_active
        user_key.deactivate()
        assert not user_key.is_active

    def test_unique_active_user_key_per_email_per_site(self):
        # Test that only one active UserKey is allowed per user and email.
        user = UserFactory()
        email = f"{user.username}@example.com"

        # Create two UserKeys with the same user and email.
        key1 = UserKeyFactory(user=user, email=email, site="GN", is_active=False)
        key2 = UserKeyFactory(user=user, email=email, site="GN", is_active=True)

        # Activate the second key, which should deactivate the first one.
        key2.activate()
        key2.refresh_from_db()
        key1.refresh_from_db()

        # Verify that only one key is active.
        assert key2.is_active
        assert not key1.is_active

    def test_multiple_inactive_keys_allowed(self):
        # Test that a user can have multiple inactive keys for the same
        # email/program.
        user = UserFactory()
        email = f"{user.username}@example.com"
        program_id = "GN-2024A-Q-1"
        UserKeyFactory(user=user, email=email, is_active=False)
        UserKeyFactory(user=user, email=email, is_active=False)
        ProgramKeyFactory(user=user, program_id=program_id, is_active=False)
        ProgramKeyFactory(user=user, program_id=program_id, is_active=False)

    def test_activating_key_deactivates_others(self):
        # Test activating one key deactivates others for the same user and
        # site.
        user = UserFactory()
        keys = [UserKeyFactory(user=user, site="GS", is_active=False) for _ in range(3)]
        keys.append(UserKeyFactory(user=user, site="GN", is_active=True))

        keys[0].activate()
        # Refresh the other keys to get the updated state from the database.
        keys[1].refresh_from_db()
        keys[2].refresh_from_db()
        keys[3].refresh_from_db()
        assert keys[0].is_active
        assert not keys[1].is_active
        assert not keys[2].is_active
        assert keys[3].is_active

        keys[1].activate()
        # Refresh keys[0] and keys[2] again.
        keys[0].refresh_from_db()
        keys[2].refresh_from_db()
        keys[3].refresh_from_db()
        assert not keys[0].is_active
        assert keys[1].is_active
        assert not keys[2].is_active
        assert keys[3].is_active

    def test_invalid_program_id_raises_error(self):
        # Test that creating a ProgramKey with an invalid program ID raises
        # ValidationError.
        user = UserFactory()
        invalid_program_ids = ["GT-2023B-X-100", "Invalid-Id", "GN-2023A-QQ-A", ""]

        for program_id in invalid_program_ids:
            program_key = ProgramKeyFactory(user=user, program_id=program_id)
            with pytest.raises(ValidationError):
                program_key.full_clean()

    def test_valid_program_id_passes_validation(self):
        # Test that creating a ProgramKey with a valid program ID does not
        # raise ValidationError.
        user = UserFactory()
        valid_program_ids = ["GN-2023A-Q-1", "GS-2023B-DD-2", "GN-2023A-FT-100"]

        for program_id in valid_program_ids:
            try:
                program_key = ProgramKeyFactory(user=user, program_id=program_id)
                program_key.full_clean()
            except ValidationError:
                pytest.fail(
                    f"ValidationError raised for valid program ID: {program_id}"
                )
