from .BaseController import BaseController
from .ProjectController import ProjectController
from models import ProcessEnums
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader, 
    PyMuPDFLoader
 )


class ProcessController(BaseController):
    def __init__(self, file_dir: str):
        
        super().__init__()

        self.file_dir = file_dir
        self.file_dir_path = ProjectController().get_project_path(file_dir=self.file_dir)

    def get_file_extension(self, filename: str)-> str:
        print(f"filename: {filename}")
        return Path(filename).suffix   
    
    def get_file_loader(self, filename: str)-> str:

        filepath = self.file_dir_path / filename
        file_ext = self.get_file_extension(filename=filename)

        if file_ext == ProcessEnums.PDF.value:
            return PyMuPDFLoader(filepath)

        elif file_ext == ProcessEnums.TXT.value:
            return TextLoader(filepath, encoding="utf-8")

        return None
    
    def get_file_content(self, filename: str)-> str:

        file_loader = self.get_file_loader(filename=filename)

        if file_loader is None:
            return ""

        return file_loader.load()

    def process_file_content(self, file_content: list, chank_size: int = 100, overlap_size: int = 20)-> str:

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chank_size,
            chunk_overlap=overlap_size,
            length_function=len
        )

        file_content_texts = [
            rec.page_content for rec in file_content
        ]

        file_content_metadata = [
            rec.metadata for rec in file_content
        ]

        chunks = text_splitter.create_documents(
           file_content_texts,
           file_content_metadata
        )

        return chunks

