from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
import urllib.parse
from PIL import Image
import os
import base64
import requests
from requests_toolbelt import MultipartEncoder
from .ezviz_stream_manage import DeviceStream
from src.utils import get_qrcode_buffer

monitor = APIRouter()

@monitor.get("/playAddress")
async def get_play_address(request: Request, device_id: str = Query(...), feishu_authorization: str = Query(None)):
    try:
        device_stream = DeviceStream(device_id)
        if device_stream.hls_address is None:
            raise ValueError("HLS address be None")
    except Exception as e:
        return JSONResponse(content={"error": f"Fail to get HLS address: {e}"}, status_code=404)
    encoded_hls_address = urllib.parse.quote(device_stream.hls_address)
    play_address = f"{request.state.public_domain}/HLSplayer/?hlsAddress={encoded_hls_address}"

    play_qrcode_buffer = get_qrcode_buffer(play_address, device_stream.start_time, device_stream.end_time)
    play_qrcode = Image.open(play_qrcode_buffer)
    os.makedirs("src/tmp/monitor", exist_ok=True)
    play_qrcode.save("src/tmp/monitor/play_qrcode.png")
    qrcode_url = f"{request.state.public_domain}/tmp/monitor/play_qrcode.png"

    play_qrcode_base64 = base64.b64encode(play_qrcode_buffer.getvalue()).decode("utf-8")

    response_data = {
        "playAddress": play_address,
        "qrcodeURL": qrcode_url,
        "qrcodeBase64": play_qrcode_base64,
        "startTime": device_stream.start_time,
        "endTime": device_stream.end_time
    }

    if feishu_authorization:
        try:
            url = "https://open.feishu.cn/open-apis/im/v1/images"
            form = {
                'image_type': 'message',
                'image': ('play_qrcode.png', play_qrcode_buffer, 'image/png')
            }
            multi_form = MultipartEncoder(form)
            headers = {
                'Authorization': feishu_authorization,
                'Content-Type': multi_form.content_type
            }
            response = requests.post(url, headers=headers, data=multi_form)
            if response.status_code == 200:
                response_data["qrcodeFeishuKey"] = response.json()["data"]["image_key"]
            else:
                return JSONResponse(content={"error": f"Fail to get qrcode feishu key: response = {response.content}"},
                                    status_code=404)
        except Exception as e:
            return JSONResponse(content={"error": f"Fail to get qrcode feishu key: {e}"}, status_code=404)

    return JSONResponse(content=response_data, status_code=200)