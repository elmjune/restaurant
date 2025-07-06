from amqtt.client import MQTTClient, ConnectError
from amqtt.session import ApplicationMessage
from typing import override


class TestMQTTClient(MQTTClient):
    """
    A subclass of `MQTTClient` that overrides certain methods
    to make it easier to inspect state for testing.
    """

    def __init__(self, fail_connection=False):
        self.subscriptions = []
        self.published = []
        self.messages: list[ApplicationMessage] = []
        self.connection_established = False
        self.fail_connection = fail_connection

        super().__init__()

    def buffer_message(self, msg: ApplicationMessage):
        """Add an `ApplicationMessage` to the message buffer that will be delivered on a future call to `deliver_message`."""
        self.messages.append(msg)

    @override
    async def connect(
        self,
        uri=None,
        cleansession=None,
        cafile=None,
        capath=None,
        cadata=None,
        additional_headers=None,
    ) -> int:
        if self.fail_connection:
            raise ConnectError()
        self.connection_established = True
        return 0

    @override
    async def deliver_message(self, timeout_duration=None) -> ApplicationMessage | None:
        return self.messages.pop(0)

    @override
    async def subscribe(self, topics: list[tuple[str, int]]) -> list[int]:
        self.subscriptions.extend(topics)
        return [0x80]

    @override
    async def publish(self, topic: str, payload: bytes, qos: int):
        self.published.append((topic, payload, bytes, qos))

    @override
    async def unsubscribe(self, topics: list[str]):
        for topic in self.subscriptions:
            if topic[0] in set(topics):
                self.subscriptions.remove(topic)

    @override
    async def disconnect(self):
        self.connection_established = False
