__all__ = ["activate_user_key", "delete_key", "create_key", "ManageKeysView"]

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import (
    HttpRequest,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView

from goats_tom.forms import ProgramKeyForm, UserKeyForm
from goats_tom.models import ProgramKey, UserKey


@login_required
def activate_user_key(
    request: HttpRequest,
    user_pk: int,
    pk: int,
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    """Activate a specified UserKey.

    Parameters
    ----------
    user_pk : `int`
        The primary key of the user.
    pk : `int`
        The primary key of the UserKey to be activated.

    Returns
    -------
    `HttpResponseRedirect | HttpResponsePermanentRedirect`
        Redirects to the manage-keys page.

    """
    key = get_object_or_404(UserKey, pk=pk)

    # Check permission: either the key belongs to the user or the user is a
    # superuser.
    if key.user.pk == request.user.pk or request.user.is_superuser:
        key.activate()
        messages.success(request, "Key activated.")
    else:
        messages.error(request, "You are not authorized to activate this key.")
        return redirect("manage-keys", pk=request.user.pk)

    return redirect("manage-keys", pk=user_pk)


@login_required
def create_key(
    request: HttpRequest,
    user_pk: int,
    key_type: str,
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    """Create either a UserKey or a ProgramKey for a specific user.

    Parameters
    ----------
    request : `HttpRequest`
        The request object containing form data.
    user_pk : `int`
        The primary key of the user for whom the key is being created.
    key_type : `str`
        The type of key to be created ('user' or 'program').

    Returns
    -------
    `HttpResponseRedirect | HttpResponsePermanentRedirect`
        Redirects to the manage-keys page.

    """
    target_user = get_object_or_404(User, pk=user_pk)

    # Check if the logged-in user is the target user or a superuser.
    if request.user != target_user and not request.user.is_superuser:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("manage-keys", pk=request.user.pk)

    key_forms = {"user_key": UserKeyForm, "program_key": ProgramKeyForm}

    key_form = key_forms.get(key_type)

    # Redirect if key type is not found.
    if not key_form:
        messages.error(request, "Invalid key type specified.")
        return redirect("manage-keys", pk=user_pk)

    # Only handle 'POST'
    if request.method == "POST":
        form = key_form(request.POST, prefix=key_type)
        if form.is_valid():
            key = form.save(commit=False)
            key.user = target_user
            key.save()
            messages.success(
                request,
                f"{key_type.replace('_', ' ').capitalize()} created successfully.",
            )
        else:
            for error in form.errors.values():
                messages.error(request, error)

    return redirect("manage-keys", pk=user_pk)


@login_required
def delete_key(
    request: HttpRequest,
    user_pk: int,
    key_type: str,
    pk: int,
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    """Delete a specified UserKey or ProgramKey for a given user.

    Parameters
    ----------
    request : `HttpRequest`
        The request object.
    user_pk : `int`
        The primary key of the user specified in the URL.
    key_type : `str`
        The type of key to delete ('user_key' or 'program_key').
    pk : `int`
        The primary key of the key to be deleted.

    Returns
    -------
    `HttpResponseRedirect | HttpResponsePermanentRedirect`
        Redirects to the manage-keys page after deletion.

    """
    key_models = {"user_key": UserKey, "program_key": ProgramKey}
    model = key_models.get(key_type)

    # Redirect if key type not found.
    if not model:
        messages.error(request, "Invalid key type specified.")
        return redirect("manage-keys", pk=user_pk)

    key = get_object_or_404(model, pk=pk)

    # Check permission: either the key belongs to the user or the user is a
    # superuser.
    if key.user.pk == request.user.pk or request.user.is_superuser:
        key.delete()
        messages.success(
            request,
            f"{key_type.replace('_', ' ').capitalize()} deleted successfully.",
        )
    else:
        messages.error(request, "You do not have permission to delete this key.")
        return redirect("manage-keys", pk=request.user.pk)

    return redirect("manage-keys", pk=user_pk)


class ManageKeysView(LoginRequiredMixin, TemplateView):
    """A Django view for managing User and Program Keys."""

    template_name = "auth/manage_keys.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the user_pk from URL kwargs, default to the logged-in user if not
        # provided.
        user_pk = self.kwargs.get("pk", self.request.user.pk)

        # Fetch the user object. If user_pk is not found, a 404 response will
        # be triggered.
        target_user = get_object_or_404(User, pk=user_pk)

        # Update the context with the target user and their keys
        context["target_user"] = target_user
        context["user_key_form"] = UserKeyForm(prefix="user_key")
        context["program_key_form"] = ProgramKeyForm(prefix="program_key")
        context["user_keys"] = UserKey.objects.filter(user=target_user)
        context["program_keys"] = ProgramKey.objects.filter(user=target_user)
        context["sites"] = ["GN", "GS"]
        return context
