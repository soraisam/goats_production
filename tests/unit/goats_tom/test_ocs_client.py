import pytest
from goats_tom.ocs_client import OCSClient
from pathlib import Path


@pytest.fixture
def client():
    """Fixture to create an OCSClient instance."""
    return OCSClient()


@pytest.fixture
def odb_xml():
    file_path = Path(__file__).parent.parent / "data" / "odb.xml"
    with open(file_path, "r") as file:
        return file.read()


@pytest.fixture
def coordinates_xml():
    file_path = Path(__file__).parent.parent / "data" / "coordinates.xml"
    with open(file_path, "r") as file:
        return file.read()


@pytest.fixture
def sequence_xml():
    file_path = Path(__file__).parent.parent / "data" / "sequence.xml"
    with open(file_path, "r") as file:
        return file.read()


def test_get_program_summary(client, odb_xml):
    # Mock the _send_odb_request method to return the fixture data.
    client._send_odb_request = lambda _: odb_xml

    result = client.get_program_summary("GS-2023B-Q-102-3")
    assert isinstance(result, dict)


def test_get_observation_summary(client, odb_xml):
    # Mock the _send_odb_request method to return the fixture data.
    client._send_odb_request = lambda _: odb_xml

    result = client.get_observation_summary("GS-2023B-Q-102-3")
    assert isinstance(result, dict)


def test_get_sequence(client, sequence_xml):
    # Mock the _send_wdba_request method to return the fixture data.
    client._send_wdba_request = lambda _, __: sequence_xml

    result = client.get_sequence("GS-2023B-Q-102-3")
    assert isinstance(result, dict)


def test_get_coordinates(client, coordinates_xml):
    # Mock the _send_wdba_request method to return the fixture data.
    client._send_wdba_request = lambda _, __: coordinates_xml

    result = client.get_coordinates("GS-2023B-Q-102-3")
    assert isinstance(result, dict)


def test__get_site_url_valid(client):
    """Test get_site_url with valid observation ID."""
    assert client._get_site_url("GS-2023B-Q-102-3") == client.site_urls["GS"]


def test__get_site_url_invalid(client):
    """Test get_site_url with invalid observation ID."""
    with pytest.raises(ValueError):
        client._get_site_url("Invalid-ID")

# TODO: Write tests for xmlrpc requests and odb requests.
