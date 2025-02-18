import aiofiles
from fastapi import (FastAPI, APIRouter, Depends, UploadFile, status, Request)
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from .schemes import PreprocesRequest
from models import ResponesSignal, ProjectModel, DataChunk, ChunkModel, AssetModel, Asset, AssetTypeEnum
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

    # store asset at db
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db
    )

    asset = Asset(
        asset_project_id=(project.id),
        asset_name=file_dir, # file id 
        asset_type=AssetTypeEnum.FILE.value,
        asset_size=file.size,
    )

    asset_record = await asset_model.create_asset(asset=asset) 

    response["file_dir"] = str(asset_record.id)

    return JSONResponse(
        status_code=status.HTTP_200_OK if is_vaild else status.HTTP_400_BAD_REQUEST, 
        content=response
    )

@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: str, process_request: PreprocesRequest):

    chunk_size = process_request.chank_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    asset_model = await AssetModel.create_instance(
            db_client=request.app.db
    )

    project_files_ids = {}
    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.id,
            asset_name=process_request.file_id
        )

        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponesSignal.FILE_ID_ERROR.value,
                }
            )

        project_files_ids = {
            asset_record.id: asset_record.asset_name
        }
    
    else:
    
        project_files = await asset_model.get_all_project_assets(
            asset_project_id=project.id,
            asset_type=AssetTypeEnum.FILE.value,
        )

        project_files_ids = {
            record.id: record.asset_name
            for record in project_files
        }

    if len(project_files_ids) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponesSignal.NO_FILES_ERROR.value,
            }
        )
    
    process_controller = ProcessController(file_dir=project_id)

    no_records = 0
    no_files = 0

    chunk_model = await ChunkModel.create_instance(
            db_client=request.app.db
    )

    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )

    for asset_id, file_id in project_files_ids.items():

        file_content = process_controller.get_file_content(filename=file_id)

        if file_content is None:
            logger.error(f"Error while processing file: {file_id}")
            continue

        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            chunk_size=chunk_size,
            overlap_size=overlap_size
        )

        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponesSignal.PROCESSING_FAILED.value
                }
            )

        file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i+1,
                chunk_project_id=project.id,
                chunk_asset_id=asset_id
            )
            for i, chunk in enumerate(file_chunks)
        ]

        no_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        no_files += 1

    return JSONResponse(
        content={
            "signal": ResponesSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records,
            "processed_files": no_files
        }
    )