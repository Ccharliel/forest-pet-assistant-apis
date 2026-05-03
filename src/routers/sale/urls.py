from tasks_se import POSPALGETDATA
from fastapi import APIRouter
from fastapi.responses import Response, JSONResponse
from config import CONFIG
import numpy as np
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from tenacity import retry, stop_after_attempt, wait_fixed
from loguru import logger

sale = APIRouter()
log = logger.bind(module="sale")
_get_sale_data_scheduler = None


@sale.get("/saleData")
@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    reraise=True
)
async def get_sale_data(period: str = ''):
    try:
        log.info(f"[Router] Trying to get sale data request: period = {period}")
        task = POSPALGETDATA(CONFIG.POSPAY_LOGIN_URL, CONFIG.POSPAL_USERNAME, CONFIG.POSPAL_PASSWORD)
        if period:
            task.set_period(period)
        task.run([{"sale": {"verbose": True, "database_url": None}}])
        result = task.results[0]
        result = result.replace([np.nan, np.inf, -np.inf], None)
        log.success(f"[Router] Successfully get sale data")
        return JSONResponse(content={"sale_data": result.to_dict(orient='records')}, status_code=200)
    except Exception as e:
        log.error(f"[Router] Failed to get sale data: {e}\nRetrying...")
        raise RuntimeError(f"Failed to get sale data: {e}")


@sale.post("/saleData/auto")
@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    reraise=True
)
async def save_sale_data_auto(point: str = ''):
    global _get_sale_data_scheduler
    try:
        log.info(f"[Router] Trying to set auto task for saving sale data request: point = {point}")
        task = POSPALGETDATA(CONFIG.POSPAY_LOGIN_URL, CONFIG.POSPAL_USERNAME, CONFIG.POSPAL_PASSWORD)
        if isinstance(_get_sale_data_scheduler, BackgroundScheduler):
            _get_sale_data_scheduler.remove_all_jobs()
            _get_sale_data_scheduler.shutdown(wait=False)
            _get_sale_data_scheduler = None
        if not point:
            point = (datetime.now() + timedelta(seconds=1)).strftime("%H:%M:%S")
        task.run_with_schedule(point=point, if_block=False,
                               task_list=[{"sale": {"verbose": True,
                                                    "database_url": CONFIG.MYSQL_DATABASE_URL}}],
                               if_with_schedule=True)
        _get_sale_data_scheduler = task.scheduler
        log.success(f"[Router] Successfully set auto task for saving sale data")
        return Response(status_code=200)
    except Exception as e:
        log.error(f"[Router] Failed to set auto task for saving sale data: {e}\nRetrying...")
        raise RuntimeError(f"Failed to set auto task for saving sale data: {e}")

