from collections.abc import Iterator

import pytest
from django.core.exceptions import ValidationError
from goats_tom.antares import GOATSANTARESBroker, GOATSANTARESBrokerForm


@pytest.mark.django_db
def test_goatsantaresbroker_form_valid():
    """
    Test the form with valid data.
    """
    form_data = {
        "esquery": {"query": "some valid query"},
        "query_name": "test",
        "broker": "ANTARES",
    }
    form = GOATSANTARESBrokerForm(data=form_data)
    assert form.is_valid(), "Form should be valid with correct esquery data."


@pytest.mark.django_db
def test_goatsantaresbroker_form_invalid():
    """
    Test the form with invalid data.
    """
    form_data = {}
    form = GOATSANTARESBrokerForm(data=form_data)
    assert not form.is_valid(), "Form should not be valid with empty esquery."

    with pytest.raises(ValidationError):
        form.clean()


@pytest.mark.django_db
def test_goatsantaresbroker_form_no_data():
    """
    Test the form with no data.
    """
    form = GOATSANTARESBrokerForm()
    assert not form.is_valid(), "Form should not be valid without data."


@pytest.mark.remote_data
def test_fetch_alerts_locusid_remote():
    broker = GOATSANTARESBroker()
    parameters = {"locusid": "ANT2020j7wo4"}  # Example parameter
    alerts = broker.fetch_alerts(parameters)
    assert isinstance(alerts, Iterator)


@pytest.mark.remote_data
def test_fetch_alerts_esquery_remote():
    broker = GOATSANTARESBroker()
    esquery = {
        "query": {
            "bool": {
                "filter": [
                    {
                        "range": {
                            "properties.num_mag_values": {
                                "gte": 50,
                                "lte": 100,
                            }
                        }
                    },
                    {"term": {"tags": "nuclear_transient"}},
                ]
            }
        }
    }
    parameters = {"esquery": esquery}  # Example parameter
    alerts = broker.fetch_alerts(parameters)
    assert isinstance(alerts, Iterator)
