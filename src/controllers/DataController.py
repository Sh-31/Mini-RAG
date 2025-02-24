from fastapi import UploadFile
from .BaseController import BaseController
from .ProjectController import ProjectController

import re
from pathlib import Path
from models import ResponesSignal

class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576 # Mb to Bytes

    def vaildate_uploaded_file(self, file: UploadFile)-> dict:
    
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return (
                False,
                ResponesSignal.FILE_TYPE_UNSUPPORTED
            )

        if (file.size / self.size_scale) > self.app_settings.File_MAX_SIZE:
            return (
                False,
                ResponesSignal.FILE_SIZE_EXCEEDED
            )       

        return (
            True,
            ResponesSignal.FILE_UPLOADED_SUCCESS
        )

    def get_clean_filename(self, filename: str)-> str:
        
        # Remove special characters except . and underscore
        cleaned_filename = re.sub(r'[^\w.]', '' , filename.strip())

        # Replace multiple spaces with underscore
        cleaned_filename = cleaned_filename.replace(" ", "_")

        return cleaned_filename

    def generate_unique_filepath(self, org_filename: str, file_dir:str):
        
        random_k = self.generate_random_string()
        file_dir_path = ProjectController().get_project_path(file_dir=file_dir)

        cleand_filename = self.get_clean_filename(filename=org_filename)

        file_path =  file_dir_path / f"{random_k}_{cleand_filename}"

        while file_path.exists():
            random_k = self.generate_random_string()
            file_path =  file_dir_path / f"{random_k}_{cleand_filename}"

        return file_path, f"{random_k}_{cleand_filename}"
 

