# Standard library imports.
import os
from pathlib import Path

# Related third party imports.
from django import forms

# Local application/library specific imports.


class GOAQueryForm(forms.Form):
    """Form to query GOA data with specific filters.

    Parameters
    ----------
    data : `dict`
        Form data as key-value pairs.
    """
    RAW_REDUCED_CHOICES = [
        ("ANY", "Any"),
        ("RAW", "Raw Only"),
        ("PREPARED", "IRAF Reduced (not Cals)"),
        ("PROCESSED_SCIENCE", "Processed Science Only"),
        ("PROCESSED_BIAS", "Processed Biases Only"),
        ("PROCESSED_FLAT", "Processed Flats Only"),
        ("PROCESSED_FRINGE", "Processed Fringe Frames Only"),
        ("PROCESSED_ARC", "Processed Arcs Only"),
        ("PROCESSED_DARK", "Processed Darks Only"),
        ("PROCESSED_STANDARD", "Processed Standards Only"),
        ("PROCESSED_SLITILLUM", "Processed Slit Illuminations Only")
    ]

    QA_STATE_CHOICES = [
        ("NotFail", "Not Fail"),
        ("Any", "Any"),
        ("Pass", "Pass"),
        ("Lucky", "Pass or Undefined"),
        ("Win", "Pass or Usable"),
        ("Usable", "Usable"),
        ("Undefined", "Undefined"),
        ("Fail", "Fail")
    ]

    raw_reduced = forms.ChoiceField(
        choices=RAW_REDUCED_CHOICES,
        label="Raw/Reduced",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    qa_state = forms.ChoiceField(
        choices=QA_STATE_CHOICES,
        label="QA State",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    filename_prefix = forms.CharField(
        label="Filename Prefix",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Leave empty for any"
        }),
        required=False
    )
    save_to = forms.CharField(
        label="Save To",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Leave empty for default"
        }),
        required=False,
        # TODO: Discuss how to save data other than TOMToolkit default.
        disabled=True
    )
    # Need input for hidden field.
    facility = forms.CharField(widget=forms.HiddenInput(), required=False)

    def is_valid(self) -> bool:
        """Validate the form.

        Returns
        -------
        `bool`
            ``True`` if the form is valid, ``False`` otherwise.
        """
        # Call the parent class's is_valid first.
        valid = super().is_valid()

        # Check if the local_path_to_store exists and is writable.
        local_path = self.cleaned_data.get("save_to", "")
        if local_path:
            local_path = Path(local_path)
            if not local_path.exists():
                self.add_error("save_to", "The path does not exist.")
                valid = False
            elif not os.access(local_path, os.W_OK):
                self.add_error("save_to", "Permission to write to the path is denied.")
                valid = False

        return valid

    def clean(self) -> None:
        """Create query_params from cleaned_data."""
        cleaned_data = super().clean()

        # Check the optional arguments.
        filename_prefix = cleaned_data.get("filename_prefix", "")
        local_path_to_store = cleaned_data.get("local_path_to_store", "")

        query_params = {
            "args": (cleaned_data["qa_state"], cleaned_data["raw_reduced"]),
            "kwargs": {}
        }

        if filename_prefix:
            query_params["kwargs"]["filepre"] = filename_prefix

        if local_path_to_store:
            query_params["kwargs"]["local_path_to_store"] = local_path_to_store

        # TODO: Switch to this when astroquery gets updated.
        # query_params["kwargs"]["raw_reduced"] = cleaned_data["raw_reduced"]

        cleaned_data["query_params"] = query_params
        self.cleaned_data = cleaned_data


class GOALoginForm(forms.Form):
    """A form to input GOA login information. This form is used to save GOA
    login details for a user.

    Attributes
    ----------
    username : `forms.CharField`
        The field for the GOA username.
    password : `forms.CharField`
        The field for the GOA password.
    """

    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            "class": "form-control"
        }),
        required=True
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control"
        }),
        required=True
    )
