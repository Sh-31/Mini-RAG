from helpers import get_settings
from pathlib import Path
import os
import random
import string
class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        self.root_path = Path(__file__).parent.parent 
        self.file_dir  = self.root_path / "assets" /"files"

    def generate_random_string(self, length:int = 12):
        return "".join(random.choices(string.ascii_lowercase + string.ascii_uppercase, k=length))
