__all__ = ["AstrodataFilter"]

import re
from typing import Any

from django.db.models import Q


class AstrodataFilter:
    """Constructs a Django Q object to filter astrodata descriptors based on a
    given expression.

    Parameters
    ----------
    absolute_tolerance : `float | int`, optional
        The absolute tolerance level for numeric comparisons.
    strict : `bool`, optional
        Whether to enforce strict exact matches or allow close matches.
    """

    logical_operations = ["AND", "OR", "NOT"]
    logical_operations_pattern = re.compile(r"\b(AND|OR|NOT)\b", flags=re.IGNORECASE)
    pattern = re.compile(
        r"(\w+)\s*([<>=!]+)\s*(\"[^\"]*\"|'[^']*'|[\w.,-]+(?:[eE][+-]?\d+)?)",
        flags=re.IGNORECASE,
    )
    operator_mapping = {
        "==": "__exact",
        "<": "__lt",
        ">": "__gt",
        "<=": "__lte",
        ">=": "__gte",
    }
    numeric_descriptors_tolerances = {
        "central_wavelength": 1e-5,
        "exposure_time": 1e-2,
    }
    absolute_tolerace = 1e-1
    field_header = "astrodata_descriptors__"
    partial_match_descriptors = ["filter_name", "detector_name", "disperser"]

    def __init__(
        self,
        absolute_tolerance: float | int | None = 1e-1,
        strict: bool | None = False,
    ) -> None:
        self.absolute_tolerace = absolute_tolerance
        self.strict = strict

    def parse_expression_to_query(self, expression: str) -> Q:
        """Parses a string containing an expression and converts it into a Django
        `Q` object.

        Parameters
        ----------
        expression : `str`
            The expression to query by.

        Returns
        -------
        `Q`
            A Django `Q` object representing the combined conditions.
        """
        # Split the expression into parts based on logical operations (AND, OR, NOT).
        parts = self.logical_operations_pattern.split(expression)
        q_object = Q()
        current_operation = "AND"  # Default operation.

        for part in parts:
            part = part.strip()  # noqa: PLW2901
            # Check if the current part is a logical operation.
            if part.upper() in self.logical_operations:
                # Update current logical operator if part is logical operator.
                current_operation = part.upper()
                continue

            # Search for matches of field, operator, and value in the part.
            match = self.pattern.search(part)
            if match:
                field, operator, value = match.groups()
                value = value.strip("\"'")

                # Check if operator is valid and map it to Django's query expression.
                if operator_match := self.operator_mapping.get(operator):
                    # Construct a Q object for the current field and value.
                    new_q = self._construct_query(field, operator_match, value)
                    # Apply the current logical operation to combine the new Q object.
                    q_object = self._apply_logical_operation(
                        q_object,
                        new_q,
                        current_operation,
                    )

        print(q_object)

        return q_object

    def _construct_query(self, field: str, operator_match: str, value: Any) -> Q:
        """Constructs a `Q` object based on the field, operator, and value, applying
        any necessary transformations or tolerances.

        Parameters
        ----------
        field : `str`
            The database field to filter on.
        operator_match : `str`
            The operator to use for filtering.
        value : `Any`
            The value to compare the field against.

        Returns
        -------
        `Q`
            A Django Q object with the appropriate filtering applied.
        """
        value = self._normalize_value(value)

        # If value is None, apply exact match only if operator is '__exact'.
        if value is None and operator_match == "__exact":
            return Q(**{self._build_descriptor_key(field, operator_match): value})

        # Custom behavior for numeric fields with tolerances.
        if (
            field in self.numeric_descriptors_tolerances
            and operator_match == "__exact"
            and not self.strict
        ):
            return self._handle_numeric_tolerance(field, value)

        # Apply partial match for specified fields when not strict.
        elif field in self.partial_match_descriptors and not self.strict:
            return Q(**{self._build_descriptor_key(field, "__icontains"): value})

        # Default behavior for other cases.
        else:
            return Q(**{self._build_descriptor_key(field, operator_match): value})

    def _normalize_value(self, value: Any) -> Any:
        """Takes in a value and returns the normalized value.

        Parameters
        ----------
        value : `Any`
            The value to normalize.

        Returns
        -------
        `Any`
            The normalized value to boolean, float, or string.
        """
        if isinstance(value, str) and value.strip().lower() in ["null", "none"]:
            return None
        try:
            return float(value)
        except ValueError:
            return (
                value.lower() == "true" if value.lower() in ["true", "false"] else value
            )

    def _handle_numeric_tolerance(self, field: str, value: Any) -> Q:
        """Handles the creation of a `Q` object for numeric fields where a tolerance is
        applied to the filtering.

        Parameters
        ----------
        field : `str`
            The database field to filter on.
        value : `float`
            The numeric value to compare the field against.

        Returns
        -------
        `Q`
            A Django Q object with the tolerance applied.
        """
        relative_tolerance = self.numeric_descriptors_tolerances[field]

        # Calculate the upper and lower bounds.
        lower_bound = value - max(
            relative_tolerance * abs(value), self.absolute_tolerace
        )
        upper_bound = value + max(
            relative_tolerance * abs(value), self.absolute_tolerace
        )

        return Q(
            **{
                self._build_descriptor_key(field, "__gte"): lower_bound,
                self._build_descriptor_key(field, "__lte"): upper_bound,
            }
        )

    def _apply_logical_operation(
        self, q_object: Q, new_q: Q, current_operation: str
    ) -> Q:
        """Applies a logical operation to combine two Q objects.

        Parameters
        ----------
        q_object : `Q`
            The current `Q` object to which the new `Q` object will be applied.
        new_q : `Q`
            The new `Q` object to apply to the current `Q` object.
        current_operation : `str`
            The logical operation to apply ('AND', 'OR', 'NOT').

        Returns
        -------
        `Q`
            The resulting `Q` object after applying the logical operation.

        Raises
        ------
        ValueError
            Raised if the current operation does not match 'AND', 'OR', or 'NOT'.
        """
        if current_operation == "AND":
            return q_object & new_q
        elif current_operation == "OR":
            return q_object | new_q
        elif current_operation == "NOT":
            return q_object & ~new_q
        else:
            raise ValueError(f"Current operation '{current_operation}' not supported.")

    def _build_descriptor_key(self, field: str, operator_match: str) -> str:
        """Builds the descriptor key to use for querying.

        Parameters
        ----------
        field : `str`
            The database field to filter on.
        operator_match : _type_
            The operator to use for filtering.

        Returns
        -------
        `str`
            The descriptor key and operator match formatted for Django `Q` query.
        """
        return f"{self.field_header}{field}{operator_match}"
