"""
考勤数据模型模块
定义考勤相关的数据结构和类
"""
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime


@dataclass
class ClockRecord:
    """打卡记录数据类"""
    time: str  # 时间字符串 "HH:MM"
    status: str  # 状态: "正常", "异常", "未打卡"
    
    def __post_init__(self):
        """数据验证"""
        if self.status not in ["正常", "异常", "未打卡"]:
            raise ValueError(f"无效的状态: {self.status}")


@dataclass
class DailyAttendance:
    """每日考勤数据类"""
    date: str  # 日期字符串 "YYYY-MM-DD"
    day_of_week: str  # 星期几: "周一" - "周日"
    day_type: str  # 日期类型: "工作日", "休息日", "节假日"
    clock_in: ClockRecord  # 上班打卡记录
    clock_out: ClockRecord  # 下班打卡记录
    is_confirmed: bool = False  # 是否已确认
    
    def __post_init__(self):
        """数据验证"""
        valid_weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        valid_day_types = ["工作日", "休息日", "节假日"]
        
        if self.day_of_week not in valid_weekdays:
            raise ValueError(f"无效的星期: {self.day_of_week}")
        if self.day_type not in valid_day_types:
            raise ValueError(f"无效的日期类型: {self.day_type}")


@dataclass
class MonthlyAttendance:
    """月度考勤数据类"""
    year_month: str  # 年月标识 "YYYY-MM"
    data: List[DailyAttendance]  # 每日考勤数据
    statistics: Dict[str, int] = field(default_factory=dict)  # 统计信息
    
    def __post_init__(self):
        """数据验证和统计计算"""
        # 验证年月格式
        try:
            datetime.strptime(self.year_month, "%Y-%m")
        except ValueError:
            raise ValueError(f"无效的年月格式: {self.year_month}")
        
        # 计算统计信息
        self._calculate_statistics()
    
    def _calculate_statistics(self):
        """计算统计信息"""
        self.statistics = {
            "total_days": len(self.data),
            "work_days": sum(1 for day in self.data if day.day_type == "工作日"),
            "rest_days": sum(1 for day in self.data if day.day_type == "休息日"),
            "holiday_days": sum(1 for day in self.data if day.day_type == "节假日"),
            "normal_clock_in": sum(1 for day in self.data if day.clock_in.status == "正常"),
            "abnormal_clock_in": sum(1 for day in self.data if day.clock_in.status == "异常"),
            "normal_clock_out": sum(1 for day in self.data if day.clock_out.status == "正常"),
            "abnormal_clock_out": sum(1 for day in self.data if day.clock_out.status == "异常"),
            "confirmed_days": sum(1 for day in self.data if day.is_confirmed)
        }
    
    def update_day(self, date: str, updated_day: DailyAttendance):
        """更新指定日期的考勤数据"""
        for i, day in enumerate(self.data):
            if day.date == date:
                self.data[i] = updated_day
                self._calculate_statistics()  # 重新计算统计信息
                return True
        return False
    
    def get_day(self, date: str) -> DailyAttendance:
        """获取指定日期的考勤数据"""
        for day in self.data:
            if day.date == date:
                return day
        raise ValueError(f"未找到日期: {date}")
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "year_month": self.year_month,
            "data": [
                {
                    "date": day.date,
                    "day_of_week": day.day_of_week,
                    "day_type": day.day_type,
                    "clock_in": {
                        "time": day.clock_in.time,
                        "status": day.clock_in.status
                    },
                    "clock_out": {
                        "time": day.clock_out.time,
                        "status": day.clock_out.status
                    },
                    "is_confirmed": day.is_confirmed
                }
                for day in self.data
            ],
            "statistics": self.statistics
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MonthlyAttendance':
        """从字典创建实例"""
        daily_attendance_list = []
        for day_data in data["data"]:
            clock_in = ClockRecord(
                time=day_data["clock_in"]["time"],
                status=day_data["clock_in"]["status"]
            )
            clock_out = ClockRecord(
                time=day_data["clock_out"]["time"],
                status=day_data["clock_out"]["status"]
            )
            daily_attendance = DailyAttendance(
                date=day_data["date"],
                day_of_week=day_data["day_of_week"],
                day_type=day_data["day_type"],
                clock_in=clock_in,
                clock_out=clock_out,
                is_confirmed=day_data["is_confirmed"]
            )
            daily_attendance_list.append(daily_attendance)
        
        return cls(
            year_month=data["year_month"],
            data=daily_attendance_list
        )
