from datetime import timedelta

import pytest
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from django.utils.crypto import get_random_string
from goats_tom.tests.factories import GOALoginFactory, TaskProgressFactory


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
