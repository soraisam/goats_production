"""Parsing Gemini IDs."""

__all__ = ["GeminiID"]

import re


class GeminiID:
    """A class to intelligently parse and store components of Gemini program
    and observation IDs.

    Attributes
    ----------
    site : `str`
        The Gemini site (GN or GS).
    semester : `str`
        The semester (e.g., 2023A).
    program_type : `str`
        The type of program (e.g., Q, DD, FT).
    program_number : `int`
        The program number.
    observation_number : `int | None`
        The observation number, present only for observation IDs.
    program_id : `str`
        The entire program ID.
    observation_id : `str | None`
        The entire observation ID if it is an observation ID.
    """

    sites = ["GS", "GN"]
    program_pattern = r"^(GN|GS)-(\d{4}[AB])-([A-Za-z]+)-(\d+)$"
    observation_pattern = r"^(GN|GS)-(\d{4}[AB])-([A-Za-z]+)-(\d+)-(\d+)$"

    def __init__(self, gemini_id: str):
        """Initializes with a Gemini ID.

        Parameters
        ----------
        gemini_id : `str`
            The Gemini ID to parse (either program or observation ID).
        """
        match = self.parse_id(gemini_id)

        self._site, self._semester, self._program_type, program_number = match.groups()[
            :4
        ]
        self._program_number = int(program_number)

        is_observation_id = len(match.groups()) == 5

        if is_observation_id:
            self._observation_number = int(match.group(5))
            self._observation_id = gemini_id
            self._program_id = gemini_id.rsplit("-", 1)[0]
        else:
            self._observation_id = None
            self._observation_number = None
            self._program_id = gemini_id

    def parse_id(self, gemini_id: str) -> re.Match:
        """Parses the provided Gemini ID and populates the class attributes.

        Parameters
        ----------
        gemini_id : `str`
            The Gemini ID to parse.

        Returns
        -------
        `re.Match`
            The regex match.

        Raises
        ------
        ValueError
            Raised if the Gemini ID does not match the expected format.
        """
        observation_match = re.match(self.observation_pattern, gemini_id)
        if observation_match:
            return observation_match

        program_match = re.match(self.program_pattern, gemini_id)
        if program_match:
            return program_match

        raise ValueError(f"Invalid Gemini ID format: '{gemini_id}'")

    def is_observation_id(self) -> bool:
        """Determines if the parsed ID is an observation ID.

        Returns
        -------
        `bool`
            `True` if the ID is an observation ID, `False` otherwise.
        """
        return self._observation_id is not None and self._observation_number is not None

    @property
    def site(self) -> str:
        """The Gemini site (GN or GS).

        Returns
        -------
        `str`
            The site code extracted from the Gemini ID.
        """
        return self._site

    @property
    def semester(self) -> str:
        """The semester (e.g., 2023A).

        Returns
        -------
        `str`
            The semester extracted from the Gemini ID.
        """
        return self._semester

    @property
    def program_type(self) -> str:
        """The type of program (e.g., Q, DD, FT).

        Returns
        -------
        `str`
            The program type extracted from the Gemini ID.
        """
        return self._program_type

    @property
    def program_number(self) -> int:
        """The program number.

        Returns
        -------
        `int`
            The program number extracted from the Gemini ID.
        """
        return self._program_number

    @property
    def observation_number(self) -> int | None:
        """The observation number, present only for observation IDs.

        Returns
        -------
        `int | None`
            The observation number extracted from the Gemini ID if available.
        """
        return self._observation_number

    @property
    def program_id(self) -> str:
        """The entire program ID.

        Returns
        -------
        `str`
            The full program ID string.
        """
        return self._program_id

    @property
    def observation_id(self) -> str | None:
        """The entire observation ID if it is an observation ID.

        Returns
        -------
        `str | None`
            The full observation ID string if available.
        """
        return self._observation_id

    @classmethod
    def is_valid_program_id(cls, program_id: str) -> bool:
        """Checks if the given string is a valid Gemini program ID.

        Parameters
        ----------
        program_id : `str`
            The program ID to validate.

        Returns
        -------
        `bool`
            `True` if the program ID is valid, `False` otherwise.
        """
        return re.match(cls.program_pattern, program_id) is not None

    @classmethod
    def is_valid_observation_id(cls, observation_id: str) -> bool:
        """Checks if the given string is a valid Gemini observation ID.

        Parameters
        ----------
        observation_id : `str`
            The observation ID to validate.

        Returns
        -------
        `bool`
            `True` if the observation ID is valid, `False` otherwise.
        """
        return re.match(cls.observation_pattern, observation_id) is not None

    @classmethod
    def is_valid(cls, gemini_id: str) -> bool:
        """Checks if the given string is a valid Gemini program or observation
        ID.

        Parameters
        ----------
        gemini_id : `str`
            The Gemini ID to validate.

        Returns
        -------
        `bool`
            `True` if the ID is valid (either a program or observation ID),
            `False` otherwise.
        """
        return cls.is_valid_program_id(gemini_id) or cls.is_valid_observation_id(
            gemini_id
        )
