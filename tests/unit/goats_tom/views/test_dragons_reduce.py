"""Test module for DRAGONS reductions."""

from unittest.mock import patch

from django.urls import reverse
from goats_tom.models import DRAGONSReduce
from goats_tom.tests.factories import (
    DRAGONSRecipeFactory,
    DRAGONSReduceFactory,
    UserFactory,
)
from goats_tom.views import DRAGONSReduceViewSet
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate


class TestDRAGONSReduceViewSet(APITestCase):
    """Class to test the `DRAGONSReduce` API view."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = UserFactory()
        self.create_view = DRAGONSReduceViewSet.as_view({"post": "create"})
        self.list_view = DRAGONSReduceViewSet.as_view({"get": "list"})
        self.detail_view = DRAGONSReduceViewSet.as_view({"get": "retrieve"})

    def authenticate(self, request):
        """Helper method to authenticate requests."""
        force_authenticate(request, user=self.user)

    @patch("goats_tom.views.dragons_reduce.run_dragons_reduce.send")
    def test_create_reduction(self, mock_run_dragons_reduce):
        """Test creating a new DRAGONS reduction."""
        recipe = DRAGONSRecipeFactory()
        data = {
            "recipe_id": recipe.id,
        }

        request = self.factory.post(reverse("dragonsreduce-list"), data)
        self.authenticate(request)

        response = self.create_view(request)

        # Check that the mock was called once
        mock_run_dragons_reduce.assert_called_once()

        assert response.status_code == status.HTTP_201_CREATED
        assert DRAGONSReduce.objects.count() == 1

    def test_list_reductions(self):
        """Test listing all DRAGONS reductions."""
        DRAGONSReduceFactory.create_batch(3)

        request = self.factory.get(reverse("dragonsreduce-list"))
        self.authenticate(request)

        response = self.list_view(request)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data.get("results")) == 3

    def test_retrieve_reduction(self):
        """Test retrieving a single DRAGONS reduction."""
        reduction = DRAGONSReduceFactory()

        request = self.factory.get(reverse("dragonsreduce-detail", args=[reduction.id]))
        self.authenticate(request)

        response = self.detail_view(request, pk=reduction.id)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == reduction.id

    def test_invalid_create_reduction(self):
        """Test creating a DRAGONS reduction with invalid recipe."""
        data = {"recipe_id": 9999}

        request = self.factory.post(reverse("dragonsreduce-list"), data, format="json")
        self.authenticate(request)

        response = self.create_view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authentication_required(self):
        """Test that authentication is required to access the view."""
        request = self.factory.get(reverse("dragonsreduce-list"))

        response = self.list_view(request)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
