from django import forms


class GOAQueryForm(forms.Form):
    """Form to query GOA data with specific filters."""

    RAW_REDUCED_CHOICES = [
        ("", "Any"),
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
        ("AnyQA", "Any"),
        ("Pass", "Pass"),
        ("Lucky", "Pass or Undefined"),
        ("Win", "Pass or Usable"),
        ("Usable", "Usable"),
        ("UndefinedQA", "Undefined"),
        ("Fail", "Fail")
    ]

    OBSERVATION_TYPES = [
        ("", "Any"),
        ("OBJECT", "Object"),
        ("BIAS", "Bias"),
        ("DARK", "Dark"),
        ("FLAT", "Flat"),
        ("ARC", "Arc"),
        ("PINHOLE", "Pinhole"),
        ("RONCHI", "Ronchi"),
        ("CAL", "Calibration"),
        ("FRINGE", "Fring"),
        ("MASK", "MOS Mask"),
        ("BPM", "BPM"),
    ]

    OBSERVATION_CLASSES = [
        ("", "Any"),
        ("science", "Science"),
        ("acq", "Acquisition"),
        ("progCal", "Program Calibration"),
        ("dayCal", "Day Calibration"),
        ("partnerCal", "Partner Calibration"),
        ("acqCal", "Acquisition Calibration")
    ]

    DOWNLOAD_CALIBRATION_CHOICES = [
        ("yes", "Yes"),
        ("no", "No"),
        ("only", "Only Calibrations")
    ]

    observation_class = forms.ChoiceField(
        label="Observation Class",
        choices=OBSERVATION_CLASSES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    observation_type = forms.ChoiceField(
        label="Observation Type",
        choices=OBSERVATION_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    raw_reduced = forms.ChoiceField(
        choices=RAW_REDUCED_CHOICES,
        label="Raw/Reduced",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
        help_text="(Select data by processing state)"
    )

    qa_state = forms.ChoiceField(
        choices=QA_STATE_CHOICES,
        label="QA State",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
        help_text="(Quality of results you wish to access)"
    )

    filename_prefix = forms.CharField(
        label="Filename Prefix",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Leave empty for any"
        }),
        required=False,
        help_text="(Specify the first part of the filename to match by)"
    )

    download_calibrations = forms.ChoiceField(
        choices=DOWNLOAD_CALIBRATION_CHOICES,
        label="Download Associated Calibrations",
        widget=forms.RadioSelect(attrs={'class': 'form-control'}),
        required=True
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

        return valid

    def clean(self) -> None:
        """Create query_params from cleaned_data."""
        cleaned_data = super().clean()

        # Check the optional arguments.
        filename_prefix = cleaned_data.get("filename_prefix", "")

        args_list = [cleaned_data["qa_state"]]

        if cleaned_data["observation_class"]:
            args_list.append(cleaned_data["observation_class"])

        if cleaned_data["observation_type"]:
            args_list.append(cleaned_data["observation_type"])

        if cleaned_data["raw_reduced"]:
            args_list.append(cleaned_data["raw_reduced"])

        query_params = {
            "args": tuple(args_list),
            "kwargs": {}
        }

        if filename_prefix:
            query_params["kwargs"]["filepre"] = filename_prefix

        query_params["kwargs"]["download_calibrations"] = cleaned_data["download_calibrations"]

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
