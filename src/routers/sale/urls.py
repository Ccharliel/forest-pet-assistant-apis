from tasks_se import AUTOGETSALE
from fastapi import APIRouter

sale = APIRouter()


@sale.get("/saleData")
async def get_sale_data(x_p: int, y_p: int, x_s: int, y_s: int, u: str, user_name: str, password: str, period: str = ''):
    try:
        task = AUTOGETSALE(x_p, y_p, x_s, y_s, u, user_name, password)
        task.login()
        if period:
            task.set_period(period)
        task.run()
        result = task.result
    except Exception as e:
        return {"error": f"Failed to get sale data: {e}"}
    return {"sale_data": result.to_dict(orient='records')}


