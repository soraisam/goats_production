import ssl
from typing import Any
import requests
import urllib3
import xmlrpc

from .ocs_parser import OCSParser

# Disable warnings about insecure HTTP connection for now.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class OCSClient:
    """A client for interacting with the Gemini Observatory's OCS
    (Observation Control System).

    This client provides methods to retrieve and parse observation sequence
    data and coordinates from the Gemini Observatory's databases.

    Attributes
    ----------
    method_names : `dict[str, str]`
        A mapping of method names for XML-RPC calls. Maps the functionality
        (like ``get_sequence``, ``get_coordinates``) to their corresponding
        XML-RPC method names.
    site_urls : `dict[str, Any]`
        The base URLs for the Gemini South (GS) and Gemini North (GN)
        observatories, including their respective hosts and port numbers.
    odb_url : `str`
        The endpoint for querying observation database (ODB) information.
    wdba_url : `str`
        The endpoint for interacting with the Web Database Access (WDBA)
        interface.
    """

    method_names = {
        "get_sequence": "WDBA_Exec.getSequence",
        "get_coordinates": "WDBA_Tcc.getCoordinates"
    }
    site_urls = {
        "GS": {
            "host": "https://gsodb.gemini.edu",
            "port": 8443
        },
        "GN": {
            "host": "https://gnodb.gemini.edu",
            "port": 8443
        }
    }
    odb_url = "/odbbrowser/observations?programReference="
    wdba_url = "/wdba"

    def __init__(self):
        self.parser = OCSParser()

    def _get_site_url(self, program_or_observation_id: str) -> dict[str, dict[str, Any]]:
        """Determines the site URL based on the program or observation ID.

        Parameters
        ----------
        program_or_observation_id : `str`
            The program or observation ID to determine the site for.

        Returns
        -------
        `dict[str, dict[str, Any]]`
            A dictionary containing the host and port of the site.

        Raises
        ------
        ValueError
            Raised if the site is not recognized in the program or observation
            ID.
        """
        for site_code, site_info in self.site_urls.items():
            if site_code in program_or_observation_id:
                return site_info

        raise ValueError(f"Site not recognized in {program_or_observation_id}")

    def _send_wdba_request(self, method_name: str, observation_id: str) -> str:
        """Sends an XML-RPC request to the server.

        Parameters
        ----------
        method_name : `str`
            The name of the method to call on the server.
        observation_id: str : `str`
            The observation ID.

        Returns
        -------
        `str`
            The response from the server as a xml string.
        """
        site_url = self._get_site_url(observation_id)
        url = self._build_wdba_url(site_url)

        # Bypass the expired certificate.
        context = ssl._create_unverified_context()

        # Get the method and call it.
        with xmlrpc.client.ServerProxy(url, context=context) as proxy:
            response = getattr(proxy, method_name)(observation_id)

        return response

    def _extract_program_id(self, observation_id: str) -> str:
        """Extracts the program ID from the observation ID.

        Parameters
        ----------
        observation_id : `str`
            The observation ID.

        Returns
        -------
        `str`
            The extracted program ID.
        """
        return "-".join(observation_id.split("-")[:-1])

    def _build_url(self, site_url: dict[str, Any]) -> str:
        """Constructs the base URL using the host and port from the site URL
        dictionary.

        Parameters
        ----------
        site_url : `dict[str, Any]`
            A dictionary containing the host and port for a site.

        Returns
        -------
        `str`
            The constructed URL combining the host and port.
        """
        return f"{site_url['host']}:{site_url['port']}"

    def _build_wdba_url(self, site_url: dict[str, Any]) -> str:
        """Constructs the full WDBA URL for a given site.

        Parameters
        ----------
        site_url : `dict[str, Any]`
            A dictionary containing the host and port for a site.

        Returns
        -------
        `str`
            The full WDBA URL for the specified site.
        """
        return f"{self._build_url(site_url)}{self.wdba_url}"

    def _build_odb_url(self, site_url: dict[str, Any], program_id: str) -> str:
        """Constructs the full ODB URL for a given site.

        Parameters
        ----------
        site_url : `dict[str, Any]`
            A dictionary containing the host and port for a site.
        program_id : `str`:
            The program ID.

        Returns
        -------
        `str`
            The full ODB URL for the specified site.
        """
        return f"{self._build_url(site_url)}{self.odb_url}{program_id}"

    def _send_odb_request(self, observation_id: str) -> str:
        """Fetches summary for a program ID from observation database.

        Parameters
        ----------
        observation_id : `str`
            The observation ID.

        Returns
        -------
        `str`
            The response from the server.
        """
        program_id = self._extract_program_id(observation_id)

        site_url = self._get_site_url(program_id)
        url = self._build_odb_url(site_url, program_id)

        # Make the HTTP request.
        # verify=False is used to bypass SSL verification.
        response = requests.get(url, verify=False)
        response.raise_for_status()

        return response.text

    def _find_observation_summary(self, parsed_response: dict[str, Any], observation_id: str
                                  ) -> dict[str, Any]:
        """Extracts a specific observation chunk from the parsed program data.

        Parameters
        ----------
        parsed_response : `dict[str, Any]`
            The parsed program data.
        observation_id : `str`
            The observation ID to search for.

        Return
        -------
        `dict[str, Any]`
            The observation data if found, otherwise an empty dictionary.
        """
        observations = parsed_response.get("observations", {}).get("observation", [])

        # Search for matching observation ID.
        for observation in observations:
            if observation.get("id") == observation_id:
                return observation

        return {}

    def get_program_summary(self, observation_id: str) -> dict[str, Any]:
        """Fetches summary for a program ID.

        Parameters
        ----------
        observation_id : `str`
            The observation ID to extract the program ID from.

        Returns
        -------
        `dict[str, Any]`
            Program summary.
        """
        response = self._send_odb_request(observation_id)
        return self.parser.parse_odb_response(response)

    def get_observation_summary(self, observation_id: str) -> dict[str, Any]:
        """Fetches summary for an observation ID.

        Parameters
        ----------
        observation_id : `str`
            The observation ID.

        Returns
        -------
        `dict[str, Any]`
            Observation summary.
        """
        response = self._send_odb_request(observation_id)
        parsed_response = self.parser.parse_odb_response(response)
        return self._find_observation_summary(parsed_response, observation_id)

    def get_sequence(self, observation_id: str) -> dict[str, Any]:
        """Fetches the sequence data for a given observation ID.

        Parameters
        ----------
        observation_id : `str`
            The observation ID to query.

        Returns
        -------
        `dict[str, Any]`
            The response from the server.
        """
        response = self._send_wdba_request(self.method_names["get_sequence"], observation_id)
        return self.parser.parse_sequence_response(response)

    def get_coordinates(self, observation_id: str) -> dict[str, Any]:
        """Fetches the coordinates for a given observation ID.

        Parameters
        ----------
        observation_id : `str`
            The observation ID to query.

        Returns
        -------
        `dict[str, Any]`
            The response from the server.
        """
        response = self._send_wdba_request(self.method_names["get_coordinates"], observation_id)
        return self.parser.parse_coordinates_response(response)
