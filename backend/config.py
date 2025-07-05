import os


class Config:
    """Object for storing typed app configuration data."""

    def __init__(
        self,
        min_order_wait: int,
        max_order_wait: int,
        broker_url: str,
        broker_username: str,
        broker_password: str,
    ):
        """Initialize a new `Config` instance with the given parameters."""
        self.min_order_wait: int = min_order_wait
        self.max_order_wait: int = max_order_wait
        self.broker_url: str = broker_url
        self.broker_username: str = broker_username
        self.broker_password: str = broker_password


def get_config_from_env() -> Config:
    """
    Create a new `Config` instance from environment variables.

    Raises:
        EnvironmentError: if an environment variable required for config creation is not set.
    """

    env_vars = [
        os.getenv("MIN_ORDER_WAIT_SECS"),
        os.getenv("MAX_ORDER_WAIT_SECS"),
        os.getenv("MQTT_BROKER_URL"),
        os.getenv("MQTT_BROKER_USERNAME"),
        os.getenv("MQTT_BROKER_PASSWORD"),
    ]

    if not all(env_vars):
        raise EnvironmentError(
            "Not all environment variables are defined. See `.env.example` for required variables."
        )

    return Config(*env_vars)
