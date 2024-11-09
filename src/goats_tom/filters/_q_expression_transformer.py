"""Module responsible for transforming the expression from the user to filter files."""

__all__ = ["_QExpressionTransformer"]
import ast
from datetime import datetime
from typing import Any

from django.db.models import Q


class _QExpressionTransformer(ast.NodeVisitor):
    """Transforms Python expressions into Django Q objects, supporting various
    operations including comparisons on datetime and numeric fields with specified
    tolerances.

    Parameters
    ----------
    strict : `bool | None`
        Whether to enforce strict exact matches or allow close and partial matches, by
        default `None`.
    """

    operator_mapping = {
        ast.Eq: "__exact",
        ast.NotEq: "__exact",  # Apply inverse to Q.
        ast.Lt: "__lt",
        ast.LtE: "__lte",
        ast.Gt: "__gt",
        ast.GtE: "__gte",
        ast.And: "AND",
        ast.Or: "OR",
    }

    datetime_descriptors_formats = {
        "ut_time": ["%H:%M:%S.%f", "%H:%M:%S"],
        "local_time": ["%H:%M:%S.%f", "%H:%M:%S"],
        "ut_date": ["%Y-%m-%d"],
        "ut_datetime": [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%f",
        ],
    }
    numeric_descriptors_tolerances = {
        "central_wavelength": 1e-5,
        "exposure_time": 1e-2,
    }
    absolute_tolerace = 1e-1

    partial_match_descriptors = ["filter_name", "detector_name", "disperser"]

    field_header = "astrodata_descriptors__"

    def __init__(self, strict: bool = False):
        self.strict = strict

        # Store current field for operations.
        self.current_field = None

    def visit_BoolOp(self, node: ast.BoolOp) -> Q:
        """Handle boolean operations by converting them into chained Django Q objects.

        Parameters
        ----------
        node : ast.BoolOp
            The AST node representing a boolean operation (AND, OR).

        Returns
        -------
        Q
            A Django Q object representing the chained conditions.
        """
        values = [self.visit(v) for v in node.values]
        if isinstance(node.op, ast.And):
            result = values[0]
            for value in values[1:]:
                result &= value
            return result
        elif isinstance(node.op, ast.Or):
            result = values[0]
            for value in values[1:]:
                result |= value
            return result
        else:
            raise ValueError(f"Unsupported logical operator: {type(node.op).__name__}")

    def visit_Compare(self, node: ast.Compare) -> Q:
        """Converts comparison nodes into Django Q objects based on the type of
        comparison.

        Parameters
        ----------
        node : `ast.Compare`
            The AST node representing a comparison operation.

        Returns
        -------
        `Q`
            A Django Q object configured according to the comparison operation.

        Raises
        ------
        ValueError
            Raised if the comparison is not a simple one-to-one comparison.
        """
        if len(node.ops) != 1:
            raise ValueError("Only single comparisons are supported.")
        left = self.visit(node.left)
        ast_operator = node.ops[0]
        django_operator = self.operator_mapping[type(ast_operator)]
        right = self.visit(node.comparators[0])

        if isinstance(ast_operator, ast.NotEq):
            return ~Q(**{f"{left}{django_operator}": right})

        if (
            isinstance(ast_operator, ast.Eq)
            and self.current_field in self.numeric_descriptors_tolerances
            and not self.strict
        ):
            return self._handle_numeric_tolerance(right)

        # Check if partial matching is required for the current field.
        if self.current_field in self.partial_match_descriptors and not self.strict:
            django_operator = "__icontains"

        return Q(**{f"{left}{django_operator}": right})

    def _normalize_string(self, value: str) -> str | bool | None:
        """Normalize and parse string values, especially for true/false or date formats.

        Parameters
        ----------
        value : `str`
            The string value to normalize.

        Returns
        -------
        `str | bool | None`
            The normalized or parsed value.
        """
        # Check if a date and needs special formatting.
        if self.current_field in self.datetime_descriptors_formats:
            return self._parse_datetime_string(value)
        lower = value.lower()
        # Convert to bool if appropriate.
        if lower in ["true", "false"]:
            return lower == "true"
        # Convert to None if appropriate.
        if lower in ["null", "none"]:
            return None
        return value

    def _handle_numeric_tolerance(self, value: float) -> Q:
        """Handles the creation of a `Q` object for numeric fields where a tolerance is
        applied to the filtering.

        Parameters
        ----------
        value : `float`
            The numeric value to compare the field against.

        Returns
        -------
        `Q`
            A Django Q object with the tolerance applied.
        """
        # Taken from DRAGONS how they handle this.
        relative_tolerance = self.numeric_descriptors_tolerances[self.current_field]

        # Calculate the upper and lower bounds.
        lower_bound = value - max(
            relative_tolerance * abs(value), self.absolute_tolerace
        )
        upper_bound = value + max(
            relative_tolerance * abs(value), self.absolute_tolerace
        )

        return Q(
            **{
                f"{self.field_header}{self.current_field}__gte": lower_bound,
                f"{self.field_header}{self.current_field}__lte": upper_bound,
            }
        )

    def visit_Name(self, node: ast.Name) -> str:
        """Process a variable name into the corresponding field reference in Django.

        Parameters
        ----------
        node : `ast.Name`
            An AST node representing a variable name.

        Returns
        -------
        `str`
            A string that prefixes the field name with a descriptor suitable for Django
            queries.
        """
        self.current_field = node.id
        return f"{self.field_header}{node.id}"

    def visit_Constant(self, node: ast.Constant) -> Any:
        """Returns the constant value from an AST Constant node.

        Parameters
        ----------
        node : `ast.Constant`
            An AST node representing a constant value.

        Returns
        -------
        `Any`
            The Python representation of the constant.
        """
        value = node.value
        return self._normalize_string(value) if isinstance(value, str) else value

    def generic_visit(self, node: ast.AST):
        """Handles all other types of nodes that are not explicitly processed.

        Parameters
        ----------
        node : `ast.AST`
            An unhandled AST node type.

        Raises
        ------
        Exception
            Raised if the node type is unsupported.
        """
        raise Exception(f"Unsupported operation: {ast.dump(node)}")

    def _parse_datetime_string(self, value: str) -> str:
        """Parse a datetime string into a formatted string based on the field's
        expected format.

        Parameters
        ----------
        value : `str`
            The datetime string to parse.

        Returns
        -------
        `str`
            The formatted datetime string if parsing is successful.

        Raises
        ------
        ValueError
            Raised if the string does not match any expected datetime format.
        """
        formats = self.datetime_descriptors_formats[self.current_field]
        for fmt in formats:
            try:
                date_obj = datetime.strptime(value, fmt)
                if self.current_field in ["ut_time", "local_time"]:
                    # Returns only the time part in ISO format.
                    return date_obj.time().isoformat()
                elif self.current_field == "ut_date":
                    # Returns only the date part.
                    return date_obj.date().isoformat()
                elif self.current_field == "ut_datetime":
                    return date_obj.isoformat()
            except ValueError:
                continue
        raise ValueError(
            f"{value} does not match any known formats for {self.current_field}"
        )
