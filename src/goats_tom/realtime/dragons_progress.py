"""Class that sends DRAGONS recipe progress."""

__all__ = ["DRAGONSProgress"]

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from goats_tom.models import DRAGONSReduce


class DRAGONSProgress:
    """Class responsible for updating DRAGONS recipe progress."""

    group_name = "dragons_group"
    func_type = "recipe.progress.message"

    @classmethod
    def create_and_send(cls, reduce: DRAGONSReduce) -> None:
        """Creates and sends the progress status of a DRAGONS recipe.

        Parameters
        ----------
        reduce : `DRAGONSReduce`
            The model instance for recipe reduce.

        """
        cls._send(
            reduce.status,
            reduce.recipe.dragons_run.id,
            reduce.recipe.id,
            reduce.id,
        )

    @classmethod
    def _send(cls, status: str, run_id: int, recipe_id: int, reduce_id: int) -> None:
        """Sends a progress update to the specified group channel.

        Parameters
        ----------
        status : `str`
            The current status of the recipe run.
        run_id : `int`
            The identifier for the run instance.
        recipe_id : `int`
            The identifier for the recipe being executed.
        reduce_id : `int`
            The identifier for the reduction process within the recipe.

        """
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            cls.group_name,
            {
                "type": cls.func_type,
                "status": status,
                "run_id": run_id,
                "recipe_id": recipe_id,
                "reduce_id": reduce_id,
            },
        )
