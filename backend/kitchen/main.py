import asyncio
import os

from dotenv import load_dotenv
from amqtt.client import MQTTClient, ClientError, ConnectError

from order_handler import OrderHandler
from util import logger


def get_broker_url() -> str:
    """
    Returns the connection URI for the MQTT broker, loaded from the environment.

    Raises:
        EnvironmentError: if the URI could not be retrieved.
    """
    broker_url = os.getenv("MQTT_BROKER_URL")
    if not broker_url:
        raise EnvironmentError("Environment variable 'MQTT_BROKER_URL' is not set.")
    return broker_url


async def main():
    logger.info("Starting restaurant backend...")
    load_dotenv()

    try:
        broker_url = get_broker_url()
    except EnvironmentError as e:
        return logger.error(f"Fatal error while retrieving broker url: {e}")

    client = MQTTClient()
    min_wait = float(os.getenv("MIN_ORDER_WAIT_SECS", "5"))
    max_wait = float(os.getenv("MAX_ORDER_WAIT_SECS", "10"))

    order_handler = OrderHandler(client, broker_url, min_wait, max_wait)

    try:
        await order_handler.connect()
    except (ClientError, ConnectError) as e:
        return logger.error(f"Fatal error while connecting to broker: {e}")

    await order_handler.loop()


if __name__ == "__main__":
    asyncio.run(main())
