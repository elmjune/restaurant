import asyncio
import logging
import os

from dotenv import load_dotenv
from amqtt.client import MQTTClient, ClientError
from amqtt.mqtt.constants import QOS_2

from config import get_config_from_env

log = logging.getLogger(__name__)


async def handle_order():
    pass


async def main():
    log.setLevel(logging.DEBUG)

    load_dotenv()
    try:
        config = get_config_from_env()
    except EnvironmentError as e:
        log.error(f"Fatal error while creating config: {e}")
        exit(1)

    client = MQTTClient()


if __name__ == "__main__":
    asyncio.run(main())
