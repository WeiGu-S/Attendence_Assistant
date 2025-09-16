"""
考勤助手包 - 自动解析考勤图片并可视化展示
"""
__version__ = "1.0.0"
__author__ = "Attendance Assistant Team"
__email__ = "dev@attendance-assistant.com"
__description__ = "考勤图片解析可视化桌面应用程序"

from .core.models import MonthlyAttendance, DailyAttendance, ClockRecord
from .core.exceptions import (
    AttendanceAssistantError,
    ImageLoadError,
    OCRProcessingError,
    DataValidationError,
    ExportError
)

__all__ = [
    "MonthlyAttendance",
    "DailyAttendance", 
    "ClockRecord",
    "AttendanceAssistantError",
    "ImageLoadError",
    "OCRProcessingError",
    "DataValidationError",
    "ExportError"
]