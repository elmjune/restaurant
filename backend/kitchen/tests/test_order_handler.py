from order_handler import OrderHandler
from .client import TestMQTTClient
from amqtt.mqtt.constants import QOS_2
from amqtt.client import ConnectError
from amqtt.session import ApplicationMessage
from asyncio import TaskGroup
from amqtt.mqtt.publish import PublishPacket, PublishPayload, PublishVariableHeader

import unittest


class OrderHandlerTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = TestMQTTClient()
        self.handler = OrderHandler(self.client, "test_broker", min_wait=0, max_wait=0)

    async def test_connect_successful(self):
        """Test a successful connection to the broker."""
        await self.handler.connect()
        self.assertTrue(self.client.connection_established)
        self.assertEqual(self.client.subscriptions, [("restaurant/order", QOS_2)])

    async def test_connect_failure(self):
        """Test a failed connection to the broker."""
        self.client.fail_connection = True
        with self.assertRaises(ConnectError):
            await self.handler.connect()
        self.assertEqual(self.client.subscriptions, [])

    async def test_close(self):
        """Test closing a connection to the broker."""
        await self.handler.connect()
        await self.handler.close()
        self.assertFalse(self.client.connection_established)
        self.assertEqual(self.client.subscriptions, [])

    async def test_order_single(self):
        """Test handling a single order."""
        msg = ApplicationMessage(0, "restaurant/order", QOS_2, b"data1", False)
        msg.publish_packet = PublishPacket(
            payload=PublishPayload(msg.data),
            variable_header=PublishVariableHeader(msg.topic, msg.packet_id),
        )
        self.client.buffer_message(msg)
        await self.handler.connect()

        async with TaskGroup() as group:
            await self.handler.listen_for_order(group)
        self.assertEqual(len(self.client.published), 1)
        await self.handler.close()

    async def test_order_multiple(self):
        """Test handling multiple orders."""
        msgs = [
            ApplicationMessage(i, "restaurant/order", QOS_2, b"data", False)
            for i in range(10)
        ]
        for msg in msgs:
            msg.publish_packet = PublishPacket(
                payload=PublishPayload(msg.data),
                variable_header=PublishVariableHeader(msg.topic, msg.packet_id),
            )
            self.client.buffer_message(msg)
        await self.handler.connect()

        async with TaskGroup() as group:
            for _ in msgs:
                await self.handler.listen_for_order(group)
        self.assertEqual(len(self.client.published), len(msgs))
        await self.handler.close()


if __name__ == "__main__":
    unittest.main()
