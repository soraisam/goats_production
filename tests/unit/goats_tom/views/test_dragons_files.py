"""Test module for a DRAGONS file."""

from django.urls import reverse
from goats_tom.tests.factories import DRAGONSFileFactory, DRAGONSRunFactory, UserFactory
from goats_tom.views import DRAGONSFilesViewSet
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate


class TestDRAGONSFilesViewSet(APITestCase):
    """Class to test the `DRAGONSFile` API view."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = UserFactory()
        self.list_view = DRAGONSFilesViewSet.as_view({"get": "list"})
        self.detail_view = DRAGONSFilesViewSet.as_view({"get": "retrieve"})
        self.update_view = DRAGONSFilesViewSet.as_view({"patch": "partial_update"})

    def authenticate(self, request):
        """Helper method to authenticate requests."""
        force_authenticate(request, user=self.user)

    def test_list_files(self):
        """Test listing all DRAGONS files."""
        DRAGONSFileFactory.create_batch(3)

        request = self.factory.get(reverse("dragonsfile-list"))
        self.authenticate(request)

        response = self.list_view(request)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data.get("results")) == 3

    def test_retrieve_file(self):
        """Test retrieving a single DRAGONS file."""
        dragons_file = DRAGONSFileFactory()

        request = self.factory.get(
            reverse("dragonsfile-detail", args=[dragons_file.id])
        )
        self.authenticate(request)

        response = self.detail_view(request, pk=dragons_file.id)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["enabled"] == dragons_file.enabled

    def test_partial_update_file(self):
        """Test partially updating a DRAGONS file."""
        dragons_file = DRAGONSFileFactory(enabled=True)
        data = {"enabled": False}

        request = self.factory.patch(
            reverse("dragonsfile-detail", args=[dragons_file.id]), data, format="json"
        )
        self.authenticate(request)

        response = self.update_view(request, pk=dragons_file.id)
        dragons_file.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert dragons_file.enabled == data["enabled"]

    def test_filter_by_dragons_run(self):
        """Test filtering DRAGONS files by DRAGONS run."""
        dragons_run = DRAGONSRunFactory()
        DRAGONSFileFactory.create_batch(2, dragons_run=dragons_run)
        DRAGONSFileFactory.create_batch(3)

        request = self.factory.get(
            reverse("dragonsfile-list"), {"dragons_run": dragons_run.pk}
        )
        self.authenticate(request)

        response = self.list_view(request)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data.get("results")) == 2

    def test_invalid_partial_update(self):
        """Test partially updating a DRAGONS file with invalid data."""
        dragons_file = DRAGONSFileFactory()
        data = {"enabled": None}  # Invalid data, enabled should be a boolean

        request = self.factory.patch(
            reverse("dragonsfile-detail", args=[dragons_file.id]), data, format="json"
        )
        self.authenticate(request)

        response = self.update_view(request, pk=dragons_file.id)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_authentication_required(self):
        """Test that authentication is required to access the view."""
        request = self.factory.get(reverse("dragonsfile-list"))

        response = self.list_view(request)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
