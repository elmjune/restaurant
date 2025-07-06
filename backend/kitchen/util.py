import logging
import sys

APP_NAME = "kitchen"

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(APP_NAME)
