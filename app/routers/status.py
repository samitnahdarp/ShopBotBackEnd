from fastapi import APIRouter
import asyncio
from app.async_tools import load_json

router = APIRouter(
    prefix="/status",
    tags=["status"]
)

@router.get("")
async def get_status():
    with open("status.json", "r") as f:
        status_data = await load_json("status.json")
    
    