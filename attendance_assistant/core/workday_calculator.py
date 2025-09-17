"""
工作日计算模块
统一处理工作日判断逻辑，包括法定节假日处理
工作日定义：周日到周五，排除国家法定节假日
"""
from datetime import datetime, date
from typing import Dict, List, Set
import json
import os


class WorkdayCalculator:
    """工作日计算器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化工作日计算器
        
        Args:
            config_path: 节假日配置文件路径
        """
        self.holidays: Dict[int, Set[str]] = {}  # 年份 -> 节假日日期集合
        self.workdays_override: Dict[int, Set[str]] = {}  # 年份 -> 调休工作日集合
        
        if config_path and os.path.exists(config_path):
            self.load_holiday_config(config_path)
    
    def load_holiday_config(self, config_path: str):
        """
        加载节假日配置文件
        
        配置文件格式示例:
        {
            "2024": {
                "holidays": ["2024-01-01", "2024-02-10", "2024-02-11", ...],
                "workdays": ["2024-02-04", "2024-02-18", ...]
            }
        }
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            for year_str, year_config in config.items():
                year = int(year_str)
                
                # 加载节假日
                if 'holidays' in year_config:
                    self.holidays[year] = set(year_config['holidays'])
                
                # 加载调休工作日
                if 'workdays' in year_config:
                    self.workdays_override[year] = set(year_config['workdays'])
                    
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            print(f"加载节假日配置失败: {e}")
    
    def is_weekend(self, date_str: str) -> bool:
        """
        判断是否为周末（仅周六）
        根据新的工作日定义，周日到周五为工作日，只有周六是周末
        
        Args:
            date_str: 日期字符串 "YYYY-MM-DD"
            
        Returns:
            bool: 是否为周末
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            # 0=Monday, 1=Tuesday, ..., 5=Saturday, 6=Sunday
            return date_obj.weekday() == 5  # 只有周六是周末
        except ValueError:
            return False
    
    def is_natural_workday(self, date_str: str) -> bool:
        """
        判断是否为自然工作日（周日到周五，不考虑节假日）
        
        Args:
            date_str: 日期字符串 "YYYY-MM-DD"
            
        Returns:
            bool: 是否为自然工作日
        """
        try:
            # 严格验证日期格式
            if not date_str or len(date_str) != 10 or date_str.count('-') != 2:
                return False
            
            parts = date_str.split('-')
            if len(parts) != 3 or len(parts[0]) != 4 or len(parts[1]) != 2 or len(parts[2]) != 2:
                return False
            
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            weekday = date_obj.weekday()  # 0=Monday, 6=Sunday
            # 周日到周五为工作日：周日(6), 周一(0), 周二(1), 周三(2), 周四(3), 周五(4)
            return weekday != 5  # 只有周六(5)不是工作日
        except ValueError:
            return False
    
    def is_holiday(self, date_str: str) -> bool:
        """
        判断是否为法定节假日
        
        Args:
            date_str: 日期字符串 "YYYY-MM-DD"
            
        Returns:
            bool: 是否为法定节假日
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year
            
            if year in self.holidays:
                return date_str in self.holidays[year]
            
            return False
        except ValueError:
            return False
    
    def is_workday_override(self, date_str: str) -> bool:
        """
        判断是否为调休工作日
        
        Args:
            date_str: 日期字符串 "YYYY-MM-DD"
            
        Returns:
            bool: 是否为调休工作日
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year
            
            if year in self.workdays_override:
                return date_str in self.workdays_override[year]
            
            return False
        except ValueError:
            return False
    
    def is_workday(self, date_str: str) -> bool:
        """
        判断是否为工作日（综合考虑自然工作日、节假日和调休）
        
        判断逻辑：
        1. 如果是调休工作日，则为工作日
        2. 如果是法定节假日，则不是工作日
        3. 否则按自然工作日判断（周日到周五）
        
        Args:
            date_str: 日期字符串 "YYYY-MM-DD"
            
        Returns:
            bool: 是否为工作日
        """
        # 调休工作日优先级最高
        if self.is_workday_override(date_str):
            return True
        
        # 法定节假日不是工作日
        if self.is_holiday(date_str):
            return False
        
        # 按自然工作日判断
        return self.is_natural_workday(date_str)
    
    def get_day_type(self, date_str: str) -> str:
        """
        获取日期类型
        
        Args:
            date_str: 日期字符串 "YYYY-MM-DD"
            
        Returns:
            str: 日期类型 "工作日", "休息日", "节假日"
        """
        # 法定节假日
        if self.is_holiday(date_str):
            return "节假日"
        
        # 调休工作日
        if self.is_workday_override(date_str):
            return "工作日"
        
        # 自然工作日/休息日
        if self.is_natural_workday(date_str):
            return "工作日"
        else:
            return "休息日"
    
    def get_workdays_in_month(self, year: int, month: int) -> List[str]:
        """
        获取指定月份的所有工作日
        
        Args:
            year: 年份
            month: 月份
            
        Returns:
            List[str]: 工作日列表
        """
        from calendar import monthrange
        
        workdays = []
        _, last_day = monthrange(year, month)
        
        for day in range(1, last_day + 1):
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            if self.is_workday(date_str):
                workdays.append(date_str)
        
        return workdays
    
    def get_workday_count_in_month(self, year: int, month: int) -> int:
        """
        获取指定月份的工作日数量
        
        Args:
            year: 年份
            month: 月份
            
        Returns:
            int: 工作日数量
        """
        return len(self.get_workdays_in_month(year, month))
    
    def add_holiday(self, date_str: str):
        """
        添加节假日
        
        Args:
            date_str: 日期字符串 "YYYY-MM-DD"
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year
            
            if year not in self.holidays:
                self.holidays[year] = set()
            
            self.holidays[year].add(date_str)
        except ValueError:
            pass
    
    def add_workday_override(self, date_str: str):
        """
        添加调休工作日
        
        Args:
            date_str: 日期字符串 "YYYY-MM-DD"
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year
            
            if year not in self.workdays_override:
                self.workdays_override[year] = set()
            
            self.workdays_override[year].add(date_str)
        except ValueError:
            pass
    
    def remove_holiday(self, date_str: str):
        """
        移除节假日
        
        Args:
            date_str: 日期字符串 "YYYY-MM-DD"
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year
            
            if year in self.holidays:
                self.holidays[year].discard(date_str)
        except ValueError:
            pass
    
    def remove_workday_override(self, date_str: str):
        """
        移除调休工作日
        
        Args:
            date_str: 日期字符串 "YYYY-MM-DD"
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year
            
            if year in self.workdays_override:
                self.workdays_override[year].discard(date_str)
        except ValueError:
            pass
    
    def save_holiday_config(self, config_path: str):
        """
        保存节假日配置到文件
        
        Args:
            config_path: 配置文件路径
        """
        config = {}
        
        # 合并所有年份的数据
        all_years = set(self.holidays.keys()) | set(self.workdays_override.keys())
        
        for year in sorted(all_years):
            config[str(year)] = {}
            
            if year in self.holidays and self.holidays[year]:
                config[str(year)]['holidays'] = sorted(list(self.holidays[year]))
            
            if year in self.workdays_override and self.workdays_override[year]:
                config[str(year)]['workdays'] = sorted(list(self.workdays_override[year]))
        
        try:
            # 确保目录存在
            if config_path and os.path.dirname(config_path):
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存节假日配置失败: {e}")


# 全局工作日计算器实例
_workday_calculator = None


def get_workday_calculator() -> WorkdayCalculator:
    """获取全局工作日计算器实例"""
    global _workday_calculator
    if _workday_calculator is None:
        # 尝试加载配置文件
        config_path = "config/holidays.json"
        _workday_calculator = WorkdayCalculator(config_path)
    return _workday_calculator


def reset_workday_calculator():
    """重置全局工作日计算器实例"""
    global _workday_calculator
    _workday_calculator = None


def is_workday(date_str: str) -> bool:
    """
    判断是否为工作日（全局函数）
    
    Args:
        date_str: 日期字符串 "YYYY-MM-DD"
        
    Returns:
        bool: 是否为工作日
    """
    return get_workday_calculator().is_workday(date_str)


def get_day_type(date_str: str) -> str:
    """
    获取日期类型（全局函数）
    
    Args:
        date_str: 日期字符串 "YYYY-MM-DD"
        
    Returns:
        str: 日期类型 "工作日", "休息日", "节假日"
    """
    return get_workday_calculator().get_day_type(date_str)