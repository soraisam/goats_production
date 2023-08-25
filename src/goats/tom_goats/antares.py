from django import forms
from django.forms.widgets import Textarea
from django.templatetags.static import static
from tom_antares.antares import ANTARESBrokerForm, ANTARESBroker


class GOATSANTARESBrokerForm(ANTARESBrokerForm):
    """A Django form class that extends ``ANTARESBrokerForm``.

    Attributes
    ----------
    esquery : `JSONField`
        A JSON field, required for receiving Elastic Search queries.
    """

    esquery = forms.JSONField(
        required=False,
        label="Elastic Search query in JSON format",
        widget=Textarea(attrs={
            "rows": 10,
            "id": "esquery"
        }),
        initial=None
    )

    class Media:
        js = (static("js/esquery.js"), )


class GOATSANTARESBroker(ANTARESBroker):
    """Extends ``ANTARESBroker`` to use GOATS Broker form."""

    form = GOATSANTARESBrokerForm
