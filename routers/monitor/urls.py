from fastapi import APIRouter, Request, Query, Response
from fastapi.responses import JSONResponse
import urllib.parse
from routers.monitor.ezviz_stream_manage import DeviceStream
from utils import get_qrcode_buffer

monitor = APIRouter()

@monitor.get("/playAddress")
async def get_play_address(request: Request, device_id: str = Query(...)):
    try:
        device_stream = DeviceStream(device_id)
        if device_stream.hls_address is None:
            raise ValueError("HLS address be None")
    except Exception as e:
        return JSONResponse(content={"error": f"Fail to get HLS address: {e}"}, status_code=404)
    encoded_hls_address = urllib.parse.quote(device_stream.hls_address)
    play_address = f"{request.state.public_domain}/HLSplayer/?hlsAddress={encoded_hls_address}"
    return JSONResponse(content={"playAddress": play_address}, status_code=200)

@monitor.get("/playAddress/qrcode")
async def get_play_qrcode(request: Request, device_id: str = Query(...)):
    try:
        device_stream = DeviceStream(device_id)
        if device_stream.hls_address is None:
            raise ValueError("HLS address be None")
    except Exception as e:
        return JSONResponse(content={"error": f"Fail to get HLS address: {e}"}, status_code=404)
    encoded_hls_address = urllib.parse.quote(device_stream.hls_address)
    play_address = f"{request.state.public_domain}/HLSplayer/?hlsAddress={encoded_hls_address}"
    play_qrcode_buffer = get_qrcode_buffer(play_address, device_stream.start_time, device_stream.end_time)
    # play_qrcode_buffer = get_qrcode_buffer(play_address)
    return Response(content=play_qrcode_buffer.getvalue() , media_type="image/png")