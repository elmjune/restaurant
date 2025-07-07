import logging
import sys

APP_NAME = "kitchen"

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s",
)
logger = logging.getLogger(APP_NAME)
