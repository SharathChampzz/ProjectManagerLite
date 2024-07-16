from fastapi import APIRouter
import datetime

router = APIRouter()

@router.get("/")
async def read_home():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"message": f"WebService is Running! Current time is {current_time}"}