from fastapi import FastAPI, APIRouter, Depends
from helpers import get_settings, Settings

base_router = APIRouter(
    prefix="/api/v1",
)

@base_router.get("/")
async def welcome(
    app_settings:Settings = Depends(get_settings),
    
    ):
    

    app_name = app_settings.APP_NAME
    api_version = app_settings.APP_VERSION

    return {
        "message": f"Welcome to {app_name} - version {api_version}!"
    }