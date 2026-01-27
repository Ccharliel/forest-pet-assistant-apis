import os
from abc import ABC, abstractmethod

class BaseConfig(ABC):
    """
    dev and pro common config
    """
    EZVIZ_TOKEN_GET_URL: str = "https://open.ys7.com/api/lapp/token/get"
    EZVIZ_STREAM_MANAGE_URL: str = "https://open.ys7.com/api/service/media/streammanage/stream"

    @property
    def EZVIZ_STREAM_LIST_URL(self) -> str:
        return f"{self.EZVIZ_STREAM_MANAGE_URL}/list"

    @property
    def EZVIZ_STREAM_ADDRESS_URL(self) -> str:
        return f"{self.EZVIZ_STREAM_MANAGE_URL}/address"

    @property
    @abstractmethod
    def EZVIZ_KEY(self) -> str:
        pass

    @property
    @abstractmethod
    def EZVIZ_SECRET(self) -> str:
        pass

class DevConfig(BaseConfig):
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        print("Development environment: loading config from .env")

    @property
    def EZVIZ_KEY(self) -> str:
        key = os.getenv("EZVIZ_KEY")
        if key is None or len(key) == 0:
            raise ValueError("EZVIZ_KEY need to be set in .env")
        return key

    @property
    def EZVIZ_SECRET(self) -> str:
        secret = os.getenv("EZVIZ_SECRET")
        if secret is None or len(secret) == 0:
            raise ValueError("EZVIZ_SECRET need to be set in .env")
        return secret

class ProdConfig(BaseConfig):
    def __init__(self):
        print("Production environment: loading config from system")

    @property
    def EZVIZ_KEY(self) -> str:
        key = os.getenv("EZVIZ_KEY")
        if key is None or len(key) == 0:
            raise ValueError("EZVIZ_KEY need to be set in system")
        return key

    @property
    def EZVIZ_SECRET(self) -> str:
        secret = os.getenv("EZVIZ_SECRET")
        if secret is None or len(secret) == 0:
            raise ValueError("EZVIZ_SECRET need to be set in system")
        return secret


def get_config() -> BaseConfig:
    """get config according to env"""

    # get env from env variable ENVIRONMENT
    env_name = os.getenv("ENVIRONMENT", "development").lower()
    config_map = {
        "development": DevConfig,
        "dev": DevConfig,
        "production": ProdConfig,
        "prod": ProdConfig,
    }
    config_class = config_map.get(env_name, DevConfig)
    return config_class()

CONFIG = get_config()

