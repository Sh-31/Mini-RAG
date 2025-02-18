from pydantic import BaseModel
from typing import Optional


class PreprocesRequest(BaseModel):
    file_id: str = None
    chank_size: Optional[int] = 100
    overlap_size: Optional[int] = 0
    do_reset: Optional[bool] = 0