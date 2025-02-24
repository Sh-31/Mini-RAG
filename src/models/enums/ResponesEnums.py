from enum import Enum

class ResponesSignal(Enum):

    FILE_VAILDTATED_SUCCESS: str = "FILE_VAILDTATED_SUCCESS"
    FILE_TYPE_UNSUPPORTED: str = "FILE_TYPE_UNSUPPORTED"
    FILE_SIZE_EXCEEDED: str = "FILE_SIZE_TOO_BIG"
    FILE_UPLOADED_SUCCESS: str = "FILE_UPLOADED_SUCCESS"
    FILE_UPLOADED_FAILED: str = "FILE_UPLOADED_FAILED"
 
    PROCESSING_SUCCESS: str = "PROCESS_SUCCESS"
    PROCESSING_FAILED: str = "PROCESS_FAILED"

    NO_FILES_ERROR : str = "NO_FILES_ERROR"
    FILE_ID_ERROR : str = "FILE_ID_ERROR"