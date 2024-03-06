"""Utilities used for websocket communication."""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def send_notification(message: str, title: str = "", color: str = "primary") -> None:
    """Sends a notification over the websocket.

    Parameters
    ----------
    message : `str`
        The body of the notification message to be sent.
    title : `str`, optional
        The title of the notification, by default "".
    color : `str`, optional
        The bootstrap color scheme to apply to the notification, by default
        "primary".
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "notification_group",
        {
            "type": "notification.message",
            "title": title,
            "message": message,
            "color": color,
        },
    )
