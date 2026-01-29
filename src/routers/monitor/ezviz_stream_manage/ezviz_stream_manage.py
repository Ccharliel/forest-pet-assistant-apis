import requests
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger
from config import CONFIG
import os

# add log
os.makedirs("logs", exist_ok=True)
logger.add(f"logs/ezviz_stream_manage.log", rotation="1 MB",
           filter=lambda record: record["file"].name == "ezviz_stream_manage.py")

# get CURRENT_DIR & ROOT_DIR
CURRENT_FILE = Path(__file__).resolve()
CURRENT_DIR = CURRENT_FILE.parent

# get ACCESS_TOKEN
def get_accessToken():
    """
    get accessToken from TOKEN_FILE or API
    """
    TOKEN_FILE = f"{CURRENT_DIR}/token.json"
    # get accessToken from TOKEN_FILE
    if os.path.exists(TOKEN_FILE):
        # TOKEN_FILE exists
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            token_data = json.load(f)
        current_timestamp_ms = time.time() * 1000
        if current_timestamp_ms < token_data["expireTime"]:
            # accessToken unexpired
            logger.info(f"Getting accessToken from {TOKEN_FILE} ......")
            return token_data["accessToken"]
    # get accessToken from API
    logger.info(f"Getting accessToken from API ......")
    token_data = get_token_data_from_api()
    if token_data is None:
        logger.critical("Cannot get valid accessToken")
        raise ValueError("Writing token data cannot be None")
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(token_data, f, indent=2)
    return token_data["accessToken"]

# EZVIZ API
def get_token_data_from_api():
    """
    successfully get token data from api: return token_data
    else: return None
    """
    try:
        data = {
            "appKey": CONFIG.EZVIZ_KEY,
            "appSecret": CONFIG.EZVIZ_SECRET,
        }
        response = requests.post(
            CONFIG.EZVIZ_TOKEN_GET_URL,
            data=data
        )
        ret = int(response.json()["code"])
        if ret != 200:
            logger.error(f"API Error getting token data: response = {response.json()}")
            return None
        token_data = response.json()["data"]
        logger.success("Successfully get token data from API")
        return token_data
    except Exception as e:
        logger.error(f"API Error getting token data: {e}")
        return None

def create_device_stream_from_api(device_serial:str, start_time:str, end_time:str):
    """
    successfully create device stream from api: return stream_id
    else: return None
    """
    try:
        ACCESS_TOKEN = get_accessToken()
        headers = {
            "accessToken": ACCESS_TOKEN,
            "deviceSerial": device_serial
        }
        params = {
            "startTime": start_time,
            "endTime": end_time
        }
        response = requests.post(
            CONFIG.EZVIZ_STREAM_MANAGE_URL,
            headers=headers,
            params=params
        )
        ret = int(response.json()["meta"]["code"])
        if ret != 200:
            logger.error(f"API Error creating device stream: response = {response.json()}")
            return None
        stream_id = response.json()["data"]["streamId"]
        logger.success("Successfully create device stream from API")
        return stream_id
    except Exception as e:
        logger.error(f"API Error creating device stream: {e}")
        return None

def get_device_stream_list_from_api(device_serial:str):
    """
    successfully get device stream list from api: return device_stream_list
    else: return None
    """
    try:
        ACCESS_TOKEN = get_accessToken()
        headers = {
            "accessToken": ACCESS_TOKEN,
            "deviceSerial": device_serial
        }
        response = requests.get(
            CONFIG.EZVIZ_STREAM_LIST_URL,
            headers=headers
        )
        ret = int(response.json()["meta"]["code"])
        if ret != 200:
            logger.error(f"API Error getting device stream list: response = {response.json()}")
            return None
        device_stream_list = response.json()["data"]
        logger.success("Successfully get device stream list from API")
        return device_stream_list
    except Exception as e:
        logger.error(f"API Error getting device stream list: {e}")
        return None

def change_stream_period_from_api(stream_id:str, start_time:str, end_time:str):
    """
    successfully change stream period from api: return True
    else: return False
    """
    try:
        ACCESS_TOKEN = get_accessToken()
        headers = {
            "accessToken": ACCESS_TOKEN
        }
        params = {
            "streamId": stream_id,
            "startTime": start_time,
            "endTime": end_time
        }
        response = requests.put(
            CONFIG.EZVIZ_STREAM_MANAGE_URL,
            headers=headers,
            params=params
        )
        ret = int(response.json()["meta"]["code"])
        if ret != 200:
            logger.error(f"API Error changing stream period: response = {response.json()}")
            return False
        logger.success("Successfully change stream period from API")
        return True
    except Exception as e:
        logger.error(f"API Error changing stream period: {e}")
        return False

def get_stream_hls_address_from_api(stream_id:str):
    """
        successfully get stream hls address from api: return stream_hls_address
        else: return None
        """
    try:
        ACCESS_TOKEN = get_accessToken()
        headers = {
            "accessToken": ACCESS_TOKEN
        }
        params = {
            "streamId": stream_id,
            "protocol": 1
        }
        response = requests.get(
            CONFIG.EZVIZ_STREAM_ADDRESS_URL,
            headers=headers,
            params=params
        )
        ret = int(response.json()["meta"]["code"])
        if ret != 200:
            logger.error(f"API Error getting stream hls address: response = {response.json()}")
            return None
        stream_hls_address = response.json()["data"]["address"]
        logger.success("Successfully get stream hls address from API")
        return stream_hls_address
    except Exception as e:
        logger.error(f"API Error getting stream hls address: {e}")
        return None

# DeviceStream object
class DeviceStream:
    def __init__(self, device_id: str):
        now = datetime.now()
        seven_days_later = now + timedelta(days=7)
        self.start_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self.end_time = seven_days_later.strftime("%Y-%m-%d %H:%M:%S")
        self.device_id = device_id
        self.stream_id = self._get_stream_id()
        self.hls_address = get_stream_hls_address_from_api(self.stream_id)

    def _get_stream_id(self):
        """
        get stream id using device id
        stream for the device id exist: return existed stream_id (refresh valid period at the same time)
        else: return new stream_id (build a new stream)
        """
        stream_list = get_device_stream_list_from_api(self.device_id)
        if stream_list is None:
            return None
        if len(stream_list) != 0:
            # stream for the device existed
            logger.info("Stream for the device Existed")
            stream_id = stream_list[0]["streamId"]
            # refresh valid period (max 7days)
            change_stream_period_from_api(stream_id, self.start_time, self.end_time)
        else:
            # stream for the device not existed
            logger.info("Stream for the device Not Existed")
            stream_id = create_device_stream_from_api(self.device_id, self.start_time, self.end_time)
        return stream_id

if __name__ == "__main__":
    serial_tmp = "BE6589690"
    tmp = DeviceStream(serial_tmp)
    print(tmp.hls_address)