from fastapi import UploadFile
from .BaseController import BaseController
from models import ResponesSignal
from pathlib import Path

class ProjectController(BaseController):
    def __init__(self):
        super().__init__()
    

    def get_project_path(self, file_dir: str):
        
        new_file_dir = self.file_dir_parent / file_dir

        if not new_file_dir.exists():

            new_file_dir.mkdir(parents=True, exist_ok=True)

        return new_file_dir
    

