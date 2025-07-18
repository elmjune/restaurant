import asyncio
import random

from asyncio import TaskGroup
from amqtt.client import MQTTClient, ClientError
from amqtt.mqtt.constants import QOS_2
from amqtt.mqtt.publish import PublishPacket

from util import logger


class OrderHandler:
    """
    A class for dispatching restaurant deliveries in response to restaurant orders.
    """

    def __init__(
        self,
        client: MQTTClient,
        broker_url: str,
        min_wait: float = 2,
        max_wait: float = 8,
    ):
        """
        Create a new `OrderHandler` instance with the given parameters.

        Args:
            client: The `MQTTClient` that should be used for all communications
            broker_url: the connection URI to the MQTT broker
            min_wait: the minimum amount of random wait time
            max_wait: the maximum amount of random wait time
        """
        self.client = client
        self.broker_url = broker_url
        self.min_wait = min_wait
        self.max_wait = max_wait

    async def connect(self):
        """
        Connect to the MQTT broker and subscribe to the appropriate topics.

        Raises:
            ConnectError: if a connection to the broker could not be established.
            ClientError: if a connection to the broker could not be established.
        """
        await self.client.connect(self.broker_url)
        await self.client.subscribe([("restaurant/order", QOS_2)])

    async def loop(self):
        """Enters a loop for handling all future restaurant orders."""
        logger.info("Listening for orders...")
        async with TaskGroup() as group:
            while True:
                try:
                    await self.listen_for_order(group)
                except Exception as e:
                    logger.error(e)
                    break

        await self.close()

    async def listen_for_order(self, group: TaskGroup, timeout=None):
        """
        Waits for the next restaurant order and creates a new Task to handle it.
        If an error occurs while listening, it logs and returns.

        Args:
            group: the `TaskGroup` that should receive the new `Task` when an order is received.
        """
        try:
            message = await self.client.deliver_message(timeout_duration=timeout)
            if not message:
                return logger.error("Failed to retrieve next message")

            packet = message.publish_packet
            if not packet:
                return logger.error(
                    "Failed to retrieve publish packet from order message"
                )

            logger.info(f"Received packet {packet.topic_name} -> {packet.data}")
            group.create_task(self.handle_order(packet))
        except ClientError as e:
            logger.error(f"Error while handling message: {e}")

    async def handle_order(self, packet: PublishPacket):
        """
        Handle a single 'order' message.

        Args:
            packet: the packet that contains all data about the published order message.
        """

        payload_bytes = packet.data
        if not payload_bytes:
            return logger.error(f"Failed to retrieve payload for packet.")

        # wait for a random amount of time (simulate work)
        logger.info(f"Preparing order for packet {packet.topic_name} -> {packet.data}")
        await asyncio.sleep(random.uniform(self.min_wait, self.max_wait))

        await self.client.publish("restaurant/deliver", payload_bytes, qos=QOS_2)
        logger.info(f"Delivered order for packet {packet.topic_name} -> {packet.data}.")

    async def close(self):
        """Close the connection to the broker."""
        await self.client.unsubscribe(["restaurant/order"])
        await self.client.disconnect()
