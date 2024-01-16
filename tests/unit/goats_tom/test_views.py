import json
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.db.models import Q
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.test import Client, TestCase
from django.urls import reverse
from goats_tom.models import GOALogin, TaskProgress
from goats_tom.tests.factories import (
    DataProductFactory,
    GOALoginFactory,
    ReducedDatumFactory,
    TaskProgressFactory,
    UserFactory,
)
from goats_tom.views import (
    GOATSDataProductDeleteView,
    ObservationRecordDeleteView,
    ongoing_tasks,
    update_brokerquery_name,
)
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase
from tom_alerts.models import BrokerQuery
from tom_dataproducts.models import DataProduct, ReducedDatum
from tom_observations.models import ObservationRecord
from tom_observations.tests.factories import ObservingRecordFactory
from tom_targets.tests.factories import SiderealTargetFactory


@pytest.fixture
def mock_request():
    return HttpRequest()


@pytest.mark.django_db
class TestUpdateBrokerQueryName:
    @patch("goats_tom.views.BrokerQuery")
    def test_update_brokerquery_name_success(self, mock_brokerquery, mock_request):
        # Mock the BrokerQuery object and its methods.
        mock_query = MagicMock()
        mock_query.parameters = {"query_name": "Old Query Name"}
        mock_query.name = "Old Query Name"

        mock_brokerquery.objects.get.return_value = mock_query

        # Mock request.
        mock_request.method = "POST"
        mock_request.POST = {"name": "New Query Name"}

        # Call the view.
        response = update_brokerquery_name(mock_request, pk=1)

        # Assertions.
        mock_brokerquery.objects.get.assert_called_with(pk=1)
        assert mock_query.name == "New Query Name"
        assert mock_query.parameters["query_name"] == "New Query Name"
        mock_query.save.assert_called_once()

        assert isinstance(response, JsonResponse)

    @patch("goats_tom.views.BrokerQuery")
    def test_update_brokerquery_name_not_found(self, mock_brokerquery, mock_request):
        mock_brokerquery.DoesNotExist = BrokerQuery.DoesNotExist
        mock_brokerquery.objects.get.side_effect = mock_brokerquery.DoesNotExist

        # Mock request.
        mock_request.method = "POST"
        mock_request.POST = {"name": "New Query Name"}

        # Call the view.
        response = update_brokerquery_name(mock_request, pk=1)

        # Assertions.
        mock_brokerquery.objects.get.assert_called_with(pk=1)
        assert isinstance(response, JsonResponse), "Response should be a JsonResponse"
        assert response.status_code == 404, "Response status code should be 404"

    def test_update_brokerquery_name_invalid_method(self, mock_request):
        # Mock request.
        mock_request.method = "GET"

        # Call the view.
        response = update_brokerquery_name(mock_request, pk=1)

        # Assertions.
        assert isinstance(response, JsonResponse)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRecentDownloadsView(TestCase):
    def test_recent_downloads(self):
        # Create completed TaskProgress instances using the factory.
        completed_tasks = TaskProgressFactory.create_batch(5, done=True)

        # Create incomplete TaskProgress instances for control.
        incomplete_tasks = TaskProgressFactory.create_batch(3, done=False)

        # Use reverse to get the URL.
        url = reverse("recent_downloads")

        # Make a GET request to the view.
        response = self.client.get(url)

        # Get the tasks from the context of the response.
        tasks_in_context = response.context["tasks"]

        # Assertions
        self.assertTrue(all(task.done for task in tasks_in_context))
        self.assertEqual(set(tasks_in_context), set(completed_tasks))
        self.assertTrue(set(incomplete_tasks).isdisjoint(set(tasks_in_context)))


class TestOngoingTasks:
    """Class to test the ongoing_tasks view."""

    @staticmethod
    def mock_queryset(*args, **kwargs):
        """Helper function to mock QuerySet behavior.

        Returns a MagicMock object that simulates Django's QuerySet.
        """
        mock = MagicMock(spec=TaskProgress.objects.none())
        mock.filter.return_value = mock
        mock.values.return_value = list(args) if args else []
        return mock

    @patch("goats_tom.views.TaskProgress")
    def test_ongoing_tasks_no_tasks(self, mock_task_progress, mock_request):
        """Test the ongoing_tasks view with no ongoing tasks."""
        mock_task_progress.objects.filter.return_value = self.mock_queryset()

        response = ongoing_tasks(mock_request)
        assert response.status_code == 200
        assert json.loads(response.content) == []

    @pytest.mark.django_db
    @patch("goats_tom.views.TaskProgress")
    def test_ongoing_tasks_with_tasks(self, mock_task_progress, mock_request):
        """Test the ongoing_tasks view with some ongoing tasks."""
        test_tasks = [
            {"task_id": task.task_id, "progress": task.progress, "status": task.status}
            for task in TaskProgressFactory.create_batch(
                5, status="running", done=False
            )
        ]
        mock_task_progress.objects.filter.return_value = self.mock_queryset(*test_tasks)

        response = ongoing_tasks(mock_request)
        assert response.status_code == 200
        assert json.loads(response.content) == test_tasks

    @pytest.mark.django_db
    @patch("goats_tom.views.TaskProgress")
    def test_ongoing_tasks_update_done_status(self, mock_task_progress, mock_request):
        """Test the ongoing_tasks view for updating the 'done' status of
        tasks.
        """
        mock_task_progress.objects.filter.return_value = self.mock_queryset()

        ongoing_tasks(mock_request)

        # Construct the call chain as it occurs in the view function.
        completed_or_failed_filter_call = call.filter(
            Q(status="completed") | Q(status="failed")
        )
        update_call = call.filter(Q(status="completed") | Q(status="failed")).update(
            done=True
        )

        # Check if the filter call was executed.
        assert completed_or_failed_filter_call in mock_task_progress.objects.mock_calls

        # Check if the entire chain (filter followed by update) was executed.
        assert update_call in mock_task_progress.objects.mock_calls


class TestGOATSDataProductDeleteView(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.client.force_login(self.user)

        # Use factories to create test objects.
        self.data_product = DataProductFactory.create()

        # Create associated ReducedDatum objects.
        ReducedDatumFactory.create_batch(2, data_product=self.data_product)
        # Verify the number of ReducedDatum objects before deletion.
        initial_reduced_datum_count = ReducedDatum.objects.filter(
            data_product=self.data_product
        ).count()
        self.assertEqual(
            initial_reduced_datum_count, 2, "Initial ReducedDatum count does not match"
        )

    def test_form_valid(self):
        # Setup the request and view.
        request = HttpRequest()
        view = GOATSDataProductDeleteView()
        view.request = request
        view.kwargs = {"pk": self.data_product.pk}
        view.object = self.data_product

        # Get the path of the associated file before deletion.
        file_path = Path(self.data_product.data.path)

        # Call the form_valid method.
        response = view.form_valid(form=MagicMock())

        # Test that the DataProduct is deleted.
        with pytest.raises(DataProduct.DoesNotExist):
            DataProduct.objects.get(pk=self.data_product.pk)

        # Test that associated ReducedDatum objects are deleted.
        self.assertEqual(
            ReducedDatum.objects.filter(data_product=self.data_product).count(), 0
        )

        # Test that the file is deleted.
        self.assertFalse(file_path.exists(), "File was not deleted")

        # Test redirection to the success URL.
        self.assertIsInstance(response, HttpResponseRedirect)


class TestObservationRecordDeleteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")

        # Create an ObservationRecord and associated DataProducts.
        # Manually create a Target instance.
        self.target = SiderealTargetFactory.create()

        # Create an ObservationRecord with the created Target.
        self.observation_record = ObservingRecordFactory.create(
            target_id=self.target.id
        )
        DataProductFactory.create_batch(2, observation_record=self.observation_record)

    def test_form_valid(self):
        # Ensure the ObservationRecord and DataProducts exist.
        self.assertIsNotNone(
            ObservationRecord.objects.filter(pk=self.observation_record.pk).first()
        )
        self.assertEqual(
            DataProduct.objects.filter(
                observation_record=self.observation_record
            ).count(),
            2,
        )

        # Setup the request and view.
        request = HttpRequest()
        request.user = self.user
        view = ObservationRecordDeleteView()
        view.request = request
        view.kwargs = {"pk": self.observation_record.pk}
        view.object = self.observation_record

        # Call the form_valid method
        response = view.form_valid(form=MagicMock())

        # Test that the ObservationRecord is deleted.
        with pytest.raises(ObservationRecord.DoesNotExist):
            ObservationRecord.objects.get(pk=self.observation_record.pk)

        # Test that associated DataProducts are deleted
        self.assertEqual(
            DataProduct.objects.filter(
                observation_record=self.observation_record
            ).count(),
            0,
        )

        # Test redirection to the success URL.
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, reverse("observations:list"))


class UserGenerateTokenViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            "superuser", "super@example.com", "password"
        )
        self.normal_user = User.objects.create_user(
            "normaluser", "normal@example.com", "password"
        )
        self.target_user = User.objects.create_user(
            "targetuser", "target@example.com", "password"
        )

    def test_superuser_generates_token(self):
        self.client.login(username="superuser", password="password")
        response = self.client.get(
            reverse("user-generate-token", kwargs={"pk": self.target_user.pk})
        )
        self.assertEqual(response.status_code, 200)

        # Check if token is created.
        token_exists = Token.objects.filter(user=self.target_user).exists()
        self.assertTrue(token_exists)

        # Verify context contains user and token.
        self.assertIn("user", response.context)
        self.assertIn("token", response.context)
        self.assertEqual(response.context["user"], self.target_user)

    def test_non_superuser_access_denied(self):
        self.client.login(username="normaluser", password="password")
        token_url = reverse("user-generate-token", kwargs={"pk": self.target_user.pk})
        login_url = reverse("login")

        # Construct the expected URL with 'next' parameter
        expected_url = f"{login_url}?next={token_url}"
        response = self.client.get(token_url)

        self.assertRedirects(
            response, expected_url, status_code=302, target_status_code=200
        )

    def test_user_not_found(self):
        self.client.login(username="superuser", password="password")
        response = self.client.get(reverse("user-generate-token", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("user-list"))

    def tearDown(self):
        self.client.logout()


class GOALoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("testuser", "test@example.com", "password")
        self.superuser = User.objects.create_superuser(
            "superuser", "super@example.com", "password"
        )
        self.url = reverse("user-goa-login", kwargs={"pk": self.user.pk})

    def test_access_by_superuser(self):
        self.client.login(username="superuser", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auth/goa_login.html")

    def test_access_by_non_superuser(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @patch("goats_tom.views.GOA")
    def test_form_valid(self, mock_goa):
        self.client.login(username="superuser", password="password")
        mock_goa.authenticated.return_value = True

        response = self.client.post(
            self.url, {"username": "testgoa", "password": "goapass"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("user-list"))
        self.assertTrue(
            GOALogin.objects.filter(user=self.user, username="testgoa").exists()
        )

        # Check success message.
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(
            "GOA login information verified and saved successfully.",
            messages[0].message,
        )

    @patch("goats_tom.views.GOA")
    def test_form_invalid(self, mock_goa):
        self.client.login(username="superuser", password="password")
        mock_goa.authenticated.return_value = False

        response = self.client.post(
            self.url, {"username": "wronguser", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("user-list"))

        # Check error message.
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(
            "Failed to verify GOA login credentials. Please try again.",
            messages[0].message,
        )

    def tearDown(self):
        self.client.logout()


class TestReceiveQueryView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="user@test.com", password="testpass"
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("receive_query")

    def test_invalid_json(self):
        data = "invalid json"
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_unrecognized_format(self):
        data = json.dumps({"unrecognized": "format"})
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_empty_data(self):
        response = self.client.post(self.url, "", content_type="application/json")
        self.assertEqual(response.status_code, 404)


class GOAQueryFormViewTest(TestCase):
    def setUp(self):
        """Set up the necessary objects for testing."""
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.target = SiderealTargetFactory.create()
        self.observation_record = ObservingRecordFactory.create(
            target_id=self.target.id
        )
        self.url = reverse("goa_query", kwargs={"pk": self.observation_record.pk})
        self.form_data = {"download_calibrations": "yes", "facility": "test_facility"}

    @patch("goats_tom.views.GOA")
    @patch("goats_tom.views.download_goa_files")
    def test_successful_submission(self, mock_download, mock_goa):
        """Test successful form submission with valid GOA credentials."""
        GOALoginFactory.create(
            user=self.user, username="goauser", password="goapassword"
        )
        self.client.login(username="testuser", password="password")

        response = self.client.post(self.url, self.form_data)

        self.assertEqual(response.status_code, 302)
        mock_download.assert_called_once()
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn("Downloading data in background. Check back soon!", messages)

    @patch("goats_tom.views.GOA")
    def test_missing_goa_credentials(self, mock_goa):
        """Test form submission with missing GOA credentials."""
        self.client.login(username="testuser", password="password")

        response = self.client.post(self.url, self.form_data)

        self.assertEqual(response.status_code, 302)
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn(
            "GOA login credentials not found. Proprietary data will not be downloaded.",
            messages,
        )

    @patch("goats_tom.views.GOA")
    def test_failed_goa_authentication(self, mock_goa):
        """Test form submission with failed GOA authentication."""
        GOALoginFactory.create(
            user=self.user, username="goauser", password="goapassword"
        )
        self.client.login(username="testuser", password="password")

        # Mock GOA authentication failure
        mock_goa.authenticated.return_value = False

        response = self.client.post(self.url, self.form_data)

        self.assertEqual(response.status_code, 302)
        messages_list = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn(
            "GOA login failed. Re-enter login credentials. "
            "Proprietary data will not be downloaded.",
            messages_list,
        )

    def test_handling_of_form_errors(self):
        """Test handling of form errors."""
        self.client.login(username="testuser", password="password")

        # Provide partially invalid form data
        form_data = {"query_params": ""}
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 302)


class GOATSDataProductDeleteViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.client.force_login(self.user)
        self.data_product = DataProductFactory.create()
        ReducedDatumFactory.create_batch(2, data_product=self.data_product)
        self.url = reverse("delete-dataproduct", kwargs={"pk": self.data_product.pk})

    def test_successful_deletion(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(DataProduct.objects.filter(pk=self.data_product.pk).exists())
        self.assertEqual(
            ReducedDatum.objects.filter(data_product=self.data_product).count(), 0
        )

    def test_deletion_of_associated_file(self):
        # Assuming your DataProduct model has a file field named 'data'.
        file_path = Path(self.data_product.data.path)
        self.assertTrue(file_path.exists())
        self.client.post(self.url)

        self.assertFalse(file_path.exists())
