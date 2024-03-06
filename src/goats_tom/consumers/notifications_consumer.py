"""Class for notifications through websocket."""

__all__ = ["NotificationsConsumer"]

import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationsConsumer(AsyncWebsocketConsumer):
    """An async WebSocket consumer that handles sending notifications to
    connected clients.

    Attributes
    ----------
    group_name : `str`
        The name of the group that this consumer handles notifications for.
    """

    group_name = "notification_group"

    async def connect(self) -> None:
        """Asynchronously adds this consumer to the notification group upon
        WebSocket connection.
        """
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code) -> None:
        """Asynchronously removes this consumer from the notification group
        upon WebSocket disconnection.
        """
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notification_message(self, event: dict) -> None:
        """Sends a notification message to the client connected through
        WebSocket.

        Parameters
        ----------
        event : `dict`
            The event dictionary containing the notification data.
        """
        # Construct the notification message.
        notification = {
            "color": event["color"],
            "title": event["title"],
            "message": event["message"],
        }

        # Send the notification message to the WebSocket
        await self.send(text_data=json.dumps(notification))
