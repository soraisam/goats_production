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
        parts = self.logical_operations_pattern.split(expression)
        q_object = Q()
        current_operation = "AND"  # Default operation

        for part in parts:
            part = part.strip()  # noqa: PLW2901
            if part.upper() in self.logical_operations:
                # Update current logical operator
                current_operation = part.upper()
                continue

            match = self.pattern.search(part)
            if not match:
                # Skip if no match is found.
                continue

            field, operator, value = match.groups()

            operator_match = self.operator_mapping.get(operator, None)
            if operator_match is None:
                # Skip if operator is not recognized.
                continue

            value = value.strip("\"'")

            new_q = self._construct_query(field, operator_match, value)

            q_object = self._apply_logical_operation(q_object, new_q, current_operation)

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
        value, is_number = self._normalize_value(value)

        # Custom behavior for numeric fields with tolerances
        if (
            field in self.numeric_descriptors_tolerances
            and not self.strict
            and is_number
        ):
            return self._handle_numeric_tolerance(field, operator_match, value)

        elif field in self.partial_match_descriptors and not self.strict:
            return Q(**{f"{self.field_header}{field}__icontains": value})

        else:
            return Q(**{f"{self.field_header}{field}{operator_match}": value})

    def _normalize_value(self, value: Any) -> tuple[Any, bool]:
        """Takes in a value and returns the normalized value, along with it is a number
        or not.

        Parameters
        ----------
        value : `Any`
            The value to normalize.

        Returns
        -------
        `tuple[Any, bool]`
            The normalized value and if it is a number or not.
        """
        try:
            value = float(value)
            is_number = True
        except ValueError:
            value = (
                value.lower() == "true" if value.lower() in ["true", "false"] else value
            )
            is_number = False
        return value, is_number

    def _handle_numeric_tolerance(
        self, field: str, operator_match: str, value: Any
    ) -> Q:
        """Handles the creation of a `Q` object for numeric fields where a tolerance is
        applied to the filtering.

        Parameters
        ----------
        field : `str`
            The database field to filter on.
        operator_match : `str`
            The operator to use for filtering, adjusted for tolerance.
        value : `float`
            The numeric value to compare the field against.

        Returns
        -------
        `Q`
            A Django Q object with the tolerance applied.
        """
        relative_tolerance = self.numeric_descriptors_tolerances[field]

        lower_bound = value - max(
            relative_tolerance * abs(value), self.absolute_tolerace
        )
        upper_bound = value + max(
            relative_tolerance * abs(value), self.absolute_tolerace
        )

        if operator_match == "__exact":
            return Q(
                **{
                    f"{self.field_header}{field}__gte": lower_bound,
                    f"{self.field_header}{field}__lte": upper_bound,
                }
            )
        else:
            return ~Q(
                **{
                    f"{self.field_header}{field}__gte": lower_bound,
                    f"{self.field_header}{field}__lte": upper_bound,
                }
            )

    def _apply_logical_operation(self, q_object: Q, new_q: Q, current_operation: str):
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
        """
        if current_operation == "AND":
            return q_object & new_q
        elif current_operation == "OR":
            return q_object | new_q
        elif current_operation == "NOT":
            return q_object & ~new_q
        else:
            raise ValueError(f"Current operation '{current_operation}' not supported.")
