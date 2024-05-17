"""Test module for DRAGONS recipes."""

from django.urls import reverse
from goats_tom.tests.factories import (
    DRAGONSRecipeFactory,
    DRAGONSRunFactory,
    UserFactory,
)
from goats_tom.views import DRAGONSRecipesViewSet
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate


class TestDRAGONSRecipesViewSet(APITestCase):
    """Class to test the `DRAGONSRecipe` API view."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = UserFactory()
        self.list_view = DRAGONSRecipesViewSet.as_view({"get": "list"})
        self.detail_view = DRAGONSRecipesViewSet.as_view({"get": "retrieve"})

    def authenticate(self, request):
        """Helper method to authenticate requests."""
        force_authenticate(request, user=self.user)

    def test_list_recipes(self):
        """Test listing all DRAGONS recipes."""
        DRAGONSRecipeFactory.create_batch(3)

        request = self.factory.get(reverse("dragonsrecipe-list"))
        self.authenticate(request)

        response = self.list_view(request)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data.get("results")) == 3

    def test_retrieve_recipe(self):
        """Test retrieving a single DRAGONS recipe."""
        dragons_recipe = DRAGONSRecipeFactory()

        request = self.factory.get(
            reverse("dragonsrecipe-detail", args=[dragons_recipe.id])
        )
        self.authenticate(request)

        response = self.detail_view(request, pk=dragons_recipe.id)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["file_type"] == dragons_recipe.file_type

    def test_filter_by_dragons_run(self):
        """Test filtering DRAGONS recipes by DRAGONS run."""
        dragons_run = DRAGONSRunFactory()
        DRAGONSRecipeFactory.create_batch(2, dragons_run=dragons_run)
        DRAGONSRecipeFactory.create_batch(3)

        request = self.factory.get(
            reverse("dragonsrecipe-list"), {"dragons_run": dragons_run.pk}
        )
        self.authenticate(request)

        response = self.list_view(request)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data.get("results")) == 2

    def test_filter_by_file_type(self):
        """Test filtering DRAGONS recipes by file type."""
        file_type = "test-file-type"
        DRAGONSRecipeFactory.create_batch(2, file_type=file_type)
        DRAGONSRecipeFactory.create_batch(3)

        request = self.factory.get(
            reverse("dragonsrecipe-list"), {"file_type": file_type}
        )
        self.authenticate(request)

        response = self.list_view(request)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data.get("results")) == 2

    def test_authentication_required(self):
        """Test that authentication is required to access the view."""
        request = self.factory.get(reverse("dragonsrecipe-list"))

        response = self.list_view(request)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
