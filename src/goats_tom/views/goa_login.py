__all__ = ["GOALoginView"]
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import FormView

from goats_tom.astroquery import Observations as GOA
from goats_tom.forms import GOALoginForm
from goats_tom.models import GOALogin


class GOALoginView(LoginRequiredMixin, FormView):
    """View to handle GOA Login form."""

    template_name = "auth/goa_login.html"
    form_class = GOALoginForm

    def get_success_url(self) -> str:
        """Get the URL to redirect to on successful form submission.

        Returns
        -------
        `str`
            The URL to redirect to.

        """
        return reverse_lazy("user-list")

    def form_valid(self, form: GOALoginForm) -> HttpResponse:
        """Handle valid form submission.

        Parameters
        ----------
        form : `GOALoginForm`
            Valid form object.

        Returns
        -------
        `HttpResponse`
            HTTP response.

        """
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = get_object_or_404(User, pk=self.kwargs["pk"])

        # Test logging in to GOA.
        GOA.login(username, password)
        if not GOA.authenticated():
            messages.error(
                self.request,
                "Failed to verify GOA login credentials. Please try again.",
            )
        else:
            messages.success(
                self.request,
                "GOA login information verified and saved successfully.",
            )

        # No matter what, logout and save credentials.
        GOA.logout()

        GOALogin.objects.update_or_create(
            user=user,
            defaults={"username": username, "password": password},
        )

        return super().form_valid(form)

    def form_invalid(self, form: GOALoginForm) -> HttpResponse:
        """Handle invalid form submission.

        Parameters
        ----------
        form : `GOALoginForm
            Invalid form object.

        Returns
        -------
        `HttpResponse`
            HTTP response.

        """
        messages.error(
            self.request,
            "Failed to save GOA login information. Please try again.",
        )
        return super().form_invalid(form)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handle GET requests.

        Parameters
        ----------
        request : `HttpRequest`
            Incoming request object.

        Returns
        -------
        `HttpResponse`
            Rendered template as HTTP response.

        """
        user = User.objects.get(pk=self.kwargs["pk"])
        form = self.form_class()

        return render(request, self.template_name, {"user": user, "form": form})
