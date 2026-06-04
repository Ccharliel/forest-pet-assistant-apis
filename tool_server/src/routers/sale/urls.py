from tasks_se import POSPALGETDATA
from fastapi import APIRouter, Request
from fastapi.responses import Response, JSONResponse
from tenacity import retry, stop_after_attempt, wait_fixed
from loguru import logger

from config import CONFIG

sale = APIRouter()
log = logger.bind(module="sale")


@sale.get("/saleData")
@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    reraise=True
)
async def get_sale_data(period: str = ''):
    try:
        log.info(f"[Router] Trying to get sale data: period = {period}")
        task = POSPALGETDATA(CONFIG.POSPAL_URL, CONFIG.POSPAL_USER_DATA)
        try:
            if period:
                task.set_period(period)
            task.run(task_list=[{"sale": {"verbose": True, "database_url": None}}])
            result = task.results[0]
        finally:
            task.close()
        log.success(f"[Router] Successfully get sale data")
        return JSONResponse(content={"sale_data": result.to_dict(orient='records')}, status_code=200)
    except Exception as e:
        log.error(f"[Router] Failed to get sale data: {e}\nRetrying...")
        raise RuntimeError(f"Failed to get sale data: {e}")


@sale.post("/saleData")
@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    reraise=True
)
async def save_sale_data(period: str = ''):
    try:
        log.info(f"[Router] Trying to save sale data: period = {period}")
        task = POSPALGETDATA(CONFIG.POSPAL_URL, CONFIG.POSPAL_USER_DATA)
        try:
            if period:
                task.set_period(period)
            task.run(task_list=[{"sale": {"verbose": True, "database_url": CONFIG.POSPAL_DATABASE_URL}}])
            result = task.results[0]
        finally:
            task.close()
        log.success(f"[Router] Successfully save sale data")
        return JSONResponse(content={"sale_data": result.to_dict(orient='records')}, status_code=200)
    except Exception as e:
        log.error(f"[Router] Failed to save sale data: {e}\nRetrying...")
        raise RuntimeError(f"Failed to save sale data: {e}")


@sale.post("/saleData/auto")
@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    reraise=True
)
async def save_sale_data_auto(request: Request, hour=None, minute=None):
    try:
        log.info(f"[Router] Trying to set auto task for saving sale data: hour = {hour}, minute = {minute}")
        task = request.app.state.pospal_scheduled_task
        task.set_scheduler("background", hour, minute)
        task.run(task_list=[{"sale": {"verbose": True, "database_url": CONFIG.POSPAL_DATABASE_URL}}])
        log.success(f"[Router] Successfully set auto task for saving sale data")
        return Response(status_code=200)
    except Exception as e:
        log.error(f"[Router] Failed to set auto task for saving sale data: {e}\nRetrying...")
        raise RuntimeError(f"Failed to set auto task for saving sale data: {e}")

