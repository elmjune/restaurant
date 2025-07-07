from order_handler import OrderHandler
from amqtt.mqtt.constants import QOS_2
from amqtt.client import MQTTClient, ConnectError
from asyncio import TaskGroup
from amqtt.broker import Broker
from amqtt.session import ApplicationMessage
import json

import unittest

BROKER_URL = "mqtt://localhost:1883"


class OrderHandlerTest(unittest.IsolatedAsyncioTestCase):
    """Unit tests for `OrderHandler`"""

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        self.broker = Broker()
        await self.broker.start()

        self.client = MQTTClient()
        self.handler = OrderHandler(self.client, BROKER_URL, min_wait=0, max_wait=0)

        self.skip_shutdown = False

    async def asyncTearDown(self):
        await super().asyncTearDown()

        await self.client.disconnect()

        if not self.skip_shutdown:
            await self.broker.shutdown()

    async def test_connect_successful(self):
        """Test a successful connection to the broker."""
        await self.handler.connect()
        self.assertEqual(len(self.broker.sessions), 1)
        self.assertEqual(len(self.broker.subscriptions), 1)

    async def test_connect_failure(self):
        """Test a failed connection to the broker."""
        self.skip_shutdown = True
        await self.broker.shutdown()
        with self.assertRaises(ConnectError):
            await self.handler.connect()
        self.assertEqual(self.broker.subscriptions, {})

    async def test_close(self):
        """Test closing a connection to the broker."""
        await self.handler.connect()
        await self.handler.close()
        self.assertFalse(self.handler.client.session.transitions.is_connected())  # type: ignore

    async def test_order_single(self):
        """Test handling a single order."""
        await self.handler.connect()

        payload = b"{'table':1,'food':'pizza'}"
        other_client = MQTTClient()
        await other_client.connect(BROKER_URL)
        await other_client.publish("restaurant/order", payload, qos=QOS_2, retain=True)
        await other_client.subscribe([("restaurant/deliver", QOS_2)])

        async def other_client_listen():
            return await other_client.deliver_message(timeout_duration=5)

        async with TaskGroup() as group:
            task1 = group.create_task(other_client_listen())
            group.create_task(self.handler.listen_for_order(group, timeout=5))

        packet = task1.result()

        if packet is None or packet.publish_packet is None:
            self.fail("a packet was not received")

        print(packet.topic)

        self.assertEqual(packet.topic, "restaurant/deliver")
        if packet.publish_packet.payload is None:
            self.fail("packet payload was not found")
        self.assertEqual(packet.publish_packet.payload.data, payload)

        await self.handler.close()
        await other_client.disconnect()

    async def test_order_multiple(self):
        """Test handling multiple orders."""
        await self.handler.connect()

        NUM_MESSAGES = 5

        payloads = [
            json.dumps({"table": i, "food": "pizza"}).encode()
            for i in range(NUM_MESSAGES)
        ]

        other_client = MQTTClient()
        await other_client.connect(BROKER_URL)
        await other_client.subscribe([("restaurant/deliver", QOS_2)])

        async def other_client_publish():
            for payload in payloads:
                await other_client.publish(
                    "restaurant/order", payload, qos=QOS_2, retain=False
                )

        async def handler_listen(group: TaskGroup):
            for _ in range(NUM_MESSAGES):
                await self.handler.listen_for_order(group, timeout=2)

        async def other_client_listen():
            packets: list[ApplicationMessage | None] = []
            for _ in range(NUM_MESSAGES):
                p = await other_client.deliver_message(timeout_duration=5)
                packets.append(p)
            return packets

        async with TaskGroup() as group:
            group.create_task(other_client_publish())
            group.create_task(handler_listen(group))
            task1 = group.create_task(other_client_listen())

        packets = task1.result()
        self.assertEqual(len(packets), NUM_MESSAGES)

        for i, packet in enumerate(packets):
            if packet is None:
                self.fail("packet is none")
            self.assertEqual(packet.topic, "restaurant/deliver")
            self.assertEqual(packet.publish_packet.payload.data, payloads[i])  # type: ignore

        await self.handler.close()
        await other_client.disconnect()


if __name__ == "__main__":
    unittest.main()
