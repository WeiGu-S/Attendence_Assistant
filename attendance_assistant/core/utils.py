"""
工具函数模块
包含各种通用的工具函数
"""
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import calendar


def validate_time_format(time_str: str) -> bool:
    """验证时间格式是否为 HH:MM"""
    if not time_str:
        return True  # 空字符串也是有效的
    
    pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
    return bool(re.match(pattern, time_str))


def normalize_time_format(time_str: str) -> str:
    """标准化时间格式为 HH:MM"""
    if not time_str:
        return ""
    
    # 移除空格
    time_str = time_str.strip()
    
    # 如果只有数字，假设是小时
    if time_str.isdigit():
        hour = int(time_str)
        if 0 <= hour <= 23:
            return f"{hour:02d}:00"
    
    # 尝试解析各种格式
    patterns = [
        r'^(\d{1,2}):(\d{2})$',  # HH:MM 或 H:MM
        r'^(\d{1,2})\.(\d{2})$',  # HH.MM 或 H.MM
        r'^(\d{1,2})-(\d{2})$',   # HH-MM 或 H-MM
        r'^(\d{1,2})(\d{2})$',    # HHMM
    ]
    
    for pattern in patterns:
        match = re.match(pattern, time_str)
        if match:
            hour, minute = match.groups()
            hour, minute = int(hour), int(minute)
            
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return f"{hour:02d}:{minute:02d}"
    
    return time_str  # 如果无法解析，返回原字符串


def extract_date_from_text(text: str) -> Optional[Dict[str, int]]:
    """从文本中提取日期信息"""
    date_info = {}
    
    # 匹配年月日
    year_month_day_pattern = r'(\d{4})年(\d{1,2})月(\d{1,2})日'
    match = re.search(year_month_day_pattern, text)
    if match:
        date_info['year'] = int(match.group(1))
        date_info['month'] = int(match.group(2))
        date_info['day'] = int(match.group(3))
        return date_info
    
    # 匹配年月
    year_month_pattern = r'(\d{4})年(\d{1,2})月'
    match = re.search(year_month_pattern, text)
    if match:
        date_info['year'] = int(match.group(1))
        date_info['month'] = int(match.group(2))
    
    # 匹配日期
    day_pattern = r'(\d{1,2})日'
    match = re.search(day_pattern, text)
    if match:
        date_info['day'] = int(match.group(1))
    
    return date_info if date_info else None


def get_weekday_chinese(date_str: str) -> str:
    """获取中文星期"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        weekday_num = date_obj.weekday()  # 0=Monday, 6=Sunday
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        return weekdays[weekday_num]
    except ValueError:
        return ""


def is_workday(date_str: str) -> bool:
    """判断是否为工作日（周日到周五）"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        weekday = date_obj.weekday()  # 0=Monday, 6=Sunday
        # 周日到周五为工作日：周日(6), 周一(0), 周二(1), 周三(2), 周四(3), 周五(4)
        return weekday != 5  # 只有周六(5)不是工作日
    except ValueError:
        return False


def get_month_date_range(year: int, month: int) -> Tuple[str, str]:
    """获取指定年月的日期范围"""
    first_day = f"{year:04d}-{month:02d}-01"
    last_day_num = calendar.monthrange(year, month)[1]
    last_day = f"{year:04d}-{month:02d}-{last_day_num:02d}"
    return first_day, last_day


def calculate_work_hours(clock_in: str, clock_out: str) -> Optional[float]:
    """计算工作时长（小时）"""
    if not clock_in or not clock_out:
        return None
    
    try:
        # 解析时间
        in_time = datetime.strptime(clock_in, "%H:%M")
        out_time = datetime.strptime(clock_out, "%H:%M")
        
        # 如果下班时间小于上班时间，说明跨天了
        if out_time < in_time:
            out_time += timedelta(days=1)
        
        # 计算时长
        duration = out_time - in_time
        return duration.total_seconds() / 3600
        
    except ValueError:
        return None


def format_duration(hours: float) -> str:
    """格式化时长显示"""
    if hours is None:
        return ""
    
    total_minutes = int(hours * 60)
    hours_part = total_minutes // 60
    minutes_part = total_minutes % 60
    
    return f"{hours_part}小时{minutes_part}分钟"


def clean_ocr_text(text: str) -> str:
    """清理OCR识别的文本"""
    if not text:
        return ""
    
    # 移除多余的空格和换行
    text = re.sub(r'\s+', ' ', text.strip())
    
    # 移除常见的OCR错误字符
    text = text.replace('|', '1')  # 竖线常被识别为1
    text = text.replace('O', '0')  # 字母O常被识别为数字0（在时间上下文中）
    
    return text


def extract_numbers_from_text(text: str) -> List[int]:
    """从文本中提取所有数字"""
    numbers = re.findall(r'\d+', text)
    return [int(num) for num in numbers]


def is_valid_date(year: int, month: int, day: int) -> bool:
    """验证日期是否有效"""
    try:
        datetime(year, month, day)
        return True
    except ValueError:
        return False


def get_color_from_status(status: str) -> str:
    """根据状态获取颜色代码"""
    color_map = {
        '正常': '#4CAF50',      # 绿色
        '异常': '#FF9800',      # 橙色
        '未打卡': '#F44336',    # 红色
        '休息日': '#E0E0E0',    # 灰色
        '节假日': '#9C27B0'     # 紫色
    }
    return color_map.get(status, '#000000')  # 默认黑色


def generate_filename_with_timestamp(prefix: str, extension: str) -> str:
    """生成带时间戳的文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """安全除法，避免除零错误"""
    if denominator == 0:
        return default
    return numerator / denominator


def calculate_attendance_rate(normal_days: int, total_work_days: int) -> float:
    """计算出勤率"""
    if total_work_days == 0:
        return 0.0
    return (normal_days / total_work_days) * 100


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """格式化百分比显示"""
    return f"{value:.{decimal_places}f}%"