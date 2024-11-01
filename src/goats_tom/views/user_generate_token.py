__all__ = ["UserGenerateTokenView"]
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from rest_framework.authtoken.models import Token
from tom_common.mixins import SuperuserRequiredMixin


class UserGenerateTokenView(SuperuserRequiredMixin, TemplateView):
    """A view that facilitates the generation of a token for a specific user,
    accessible only by superusers.

    Attributes
    ----------
    template_name : `str`
        The name of the template to be used in this view.

    """

    template_name = "auth/generate_token.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handles the GET request to generate a token for a user.

        If the user making the request is a superuser, any existing tokens
        associated with the user identified by the primary key in the URL are
        deleted and a new token is generated.

        Parameters
        ----------
        request : `HttpRequest`
            The request instance.

        Returns
        -------
        `HttpResponse`
            A response instance containing the rendered template with user and
            token context, or a URL pointing to the "user-list" view if the
            requester is not a superuser.

        """
        try:
            user = User.objects.get(pk=self.kwargs["pk"])
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("user-list")

        if not request.user.is_superuser:
            messages.error(
                request,
                "You do not have permission to generate a token for this user.",
            )
            return redirect("user-list")

        # Superuser logic for generating token
        Token.objects.filter(user=user).delete()
        token, _ = Token.objects.get_or_create(user=user)
        return render(request, self.template_name, {"user": user, "token": token})
