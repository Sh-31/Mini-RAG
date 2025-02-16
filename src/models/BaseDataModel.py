from helpers import get_settings


class BaseDataModel:

    def __init__(self, db_client: str):
        self.app_settings = get_settings()
        self.db_client = db_client