from abc import ABC, abstractmethod
from pathlib import Path
from loguru import logger
import os
from typing import Mapping

os.makedirs("logs", exist_ok=True)
logger.add(f"logs/config.log", rotation="1 MB",
           filter=lambda record: record["file"].name == "config.py")

LOG_DIR = os.path.join(Path(__file__).resolve().parent, "logs")
print(f"LOG_DIR (tool-server): {LOG_DIR}")


class BaseConfig(ABC):
    """
    dev and pro common config
    """
    EZVIZ_TOKEN_GET_URL: str = "https://open.ys7.com/api/lapp/token/get"
    EZVIZ_STREAM_MANAGE_URL: str = "https://open.ys7.com/api/service/media/streammanage/stream"
    POSPAL_URL: str = "https://beta33.pospal.cn"

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
    
    @property
    @abstractmethod
    def POSPAL_USER_DATA(self) -> str:
        pass

    @property
    @abstractmethod
    def POSPAL_DATABASE_URL(self) -> str:
        pass
    

class DevConfig(BaseConfig):
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("Development environment: loading config from .env")

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

    @property
    def POSPAL_USER_DATA(self) -> Mapping[str, str | None]:
        username = os.getenv("POSPAL_USERNAME")
        password = os.getenv("POSPAL_PASSWORD")
        if username is None or len(username) == 0:
            raise ValueError("POSPAL_USERNAME need to be set in .env")
        if password is None or len(password) == 0:
            raise ValueError("POSPAL_PASSWORD need to be set in .env")
        return {"username": username, "password": password}
    
    @property
    def POSPAL_DATABASE_URL(self) -> str:
        url = os.getenv("POSPAL_DATABASE_URL")
        if url is None or len(url) == 0:
            raise ValueError("POSPAL_DATABASE_URL need to be set in .env")
        return url


class ProdConfig(BaseConfig):
    def __init__(self):
        logger.info("Production environment: loading config from system")

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

    @property
    def POSPAL_USER_DATA(self) -> Mapping[str, str | None]:
        username = os.getenv("POSPAL_USERNAME")
        password = os.getenv("POSPAL_PASSWORD")
        if username is None or len(username) == 0:
            raise ValueError("POSPAL_USERNAME need to be set in system")
        if password is None or len(password) == 0:
            raise ValueError("POSPAL_PASSWORD need to be set in system")
        return {"username": username, "password": password}

    @property
    def POSPAL_DATABASE_URL(self) -> str:
        url = os.getenv("POSPAL_DATABASE_URL")
        if url is None or len(url) == 0:
            raise ValueError("POSPAL_DATABASE_URL need to be set in system")
        return url


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
