import aiofiles
from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import DataController, ProjectController
from models import ResponesSignal
import logging

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)

@data_router.post("/upload/{file_id}")
async def upload_data(
    file_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings),
    ):

    data_controller = DataController()

    is_vaild, signal = data_controller.vaildate_uploaded_file(file=file)

    if is_vaild:

        new_filename = data_controller.generate_unique_filename(
            org_filename=file.filename, 
            project_name=file_id
        )

        try:
            async with aiofiles.open(new_filename, "wb") as buffer:
                while check := await file.read(app_settings.FILE_DEFAULT_CHECK_SIZE):
                    await buffer.write(check)
        except Exception as e:
            logger.error(f"Error while uploading file: {e}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST, 
                content={
                    "signal": ResponesSignal.FILE_UPLOADED_FAILED.value,
                }
            )

    return JSONResponse(
        status_code=status.HTTP_200_OK if is_vaild else status.HTTP_400_BAD_REQUEST, 
        content={
            "signal": signal.value
        }
    )
