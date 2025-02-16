import aiofiles
from fastapi import (FastAPI, APIRouter, Depends, UploadFile, status, Request)
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from .schemes import PreprocesRequest
from models import ResponesSignal, ProjectModel, DataChunk, ChunkModel
import logging

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)

@data_router.post("/upload/{file_dir}")
async def upload_data(
    request: Request,
    file_dir: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings),
    ):

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db
    )

    project = await project_model.get_project_or_create_one(
        project_id=file_dir
    )

    data_controller = DataController()
    is_vaild, signal = data_controller.vaildate_uploaded_file(file=file)
    response = {}

    if is_vaild:

        new_filename, file_dir = data_controller.generate_unique_filepath(
            org_filename=file.filename, 
            file_dir=file_dir
        )

        response["file_dir"] = file_dir

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

    response["signal"] = signal.value

    return JSONResponse(
        status_code=status.HTTP_200_OK if is_vaild else status.HTTP_400_BAD_REQUEST, 
        content=response
    )

@data_router.post("/process/{file_dir}")
async def process_data(request: Request, file_dir: str, process_request: PreprocesRequest):

    file_id = process_request.file_id
    chunk_size = process_request.chank_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db
    )

    project = await project_model.get_project_or_create_one(
        project_id=file_dir
    )

    process_controller = ProcessController(file_dir=file_dir)
    file_content = process_controller.get_file_content(filename=file_id)

    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        chank_size=chunk_size, 
        overlap_size=overlap_size
    )
    
    if len(file_chunks) == 0 or file_chunks is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponesSignal.PROCESSING_FAILED.value,
            }
        )

    file_chunks_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i+1,
            chunk_project_id=project.id,
        )
        for i, chunk in enumerate(file_chunks)
    ]

    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.db
    )

    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )

    no_records = await chunk_model.insert_many_chunks(chunks=file_chunks_records)

    return JSONResponse(
        content={
            "signal": ResponesSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records
        }
    )