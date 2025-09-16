"""
自定义异常类模块
定义应用程序中使用的各种异常
"""


class AttendanceAssistantError(Exception):
    """考勤助手基础异常类"""
    pass


class ImageLoadError(AttendanceAssistantError):
    """图片加载失败异常"""
    def __init__(self, message: str, image_path: str = None):
        super().__init__(message)
        self.image_path = image_path


class OCRProcessingError(AttendanceAssistantError):
    """OCR识别错误异常"""
    def __init__(self, message: str, image_data=None):
        super().__init__(message)
        self.image_data = image_data


class DataValidationError(AttendanceAssistantError):
    """数据验证错误异常"""
    def __init__(self, message: str, invalid_data=None):
        super().__init__(message)
        self.invalid_data = invalid_data


class ExportError(AttendanceAssistantError):
    """数据导出错误异常"""
    def __init__(self, message: str, file_path: str = None):
        super().__init__(message)
        self.file_path = file_path


class ConfigurationError(AttendanceAssistantError):
    """配置错误异常"""
    def __init__(self, message: str, config_key: str = None):
        super().__init__(message)
        self.config_key = config_key


class TableDetectionError(AttendanceAssistantError):
    """表格检测错误异常"""
    def __init__(self, message: str, image_data=None):
        super().__init__(message)
        self.image_data = image_data


class CellExtractionError(AttendanceAssistantError):
    """单元格提取错误异常"""
    def __init__(self, message: str, cell_info=None):
        super().__init__(message)
        self.cell_info = cell_info