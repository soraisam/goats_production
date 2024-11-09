"""Module responsible for interfacing with the parser and transformer."""

__all__ = ["AstrodataFilter"]

import ast

from django.db.models import Q

from goats_tom.filters._q_expression_transformer import _QExpressionTransformer


class AstrodataFilter:
    """Constructs a Django Q object to filter astrodata descriptors based on a given
    expression."""

    @staticmethod
    def parse(expression: str, strict: bool = False) -> Q | None:
        """Parse the expression into a Django Q object.

        Parameters
        ----------
        expression : `str`
            The expression to parse.
        strict : `bool`, optional
            Whether to return strict queries, by default `False`.

        Returns
        -------
        `Q | None`
            A Django Q object of the expression if valid, else `None`.
        """
        if not expression.strip():
            # Query all files if no filter.
            return Q()

        try:
            tree = ast.parse(expression, mode="eval")
            transformer = _QExpressionTransformer(strict=strict)
            return transformer.visit(tree.body)
        except SyntaxError:
            return None
