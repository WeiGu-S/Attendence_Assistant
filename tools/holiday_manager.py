"""
节假日管理工具
用于管理和维护国家法定节假日配置
"""
import json
import os
from datetime import datetime, date
from typing import Dict, List, Set, Optional
from pathlib import Path


class HolidayManager:
    """节假日管理器"""
    
    def __init__(self, config_path: str = "config/holidays.json"):
        """
        初始化节假日管理器
        
        Args:
            config_path: 节假日配置文件路径
        """
        self.config_path = config_path
        self.holidays: Dict[int, Set[str]] = {}
        self.workdays: Dict[int, Set[str]] = {}
        self.load_config()
    
    def load_config(self):
        """加载节假日配置"""
        if not os.path.exists(self.config_path):
            print(f"配置文件不存在: {self.config_path}")
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            for year_str, year_config in config.items():
                year = int(year_str)
                
                # 加载节假日
                if 'holidays' in year_config:
                    self.holidays[year] = set(year_config['holidays'])
                
                # 加载调休工作日
                if 'workdays' in year_config:
                    self.workdays[year] = set(year_config['workdays'])
            
            print(f"成功加载节假日配置，包含 {len(self.holidays)} 年的数据")
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"加载节假日配置失败: {e}")
    
    def save_config(self):
        """保存节假日配置"""
        config = {}
        
        # 合并所有年份的数据
        all_years = set(self.holidays.keys()) | set(self.workdays.keys())
        
        for year in sorted(all_years):
            config[str(year)] = {}
            
            if year in self.holidays and self.holidays[year]:
                config[str(year)]['holidays'] = sorted(list(self.holidays[year]))
            
            if year in self.workdays and self.workdays[year]:
                config[str(year)]['workdays'] = sorted(list(self.workdays[year]))
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            print(f"节假日配置已保存到: {self.config_path}")
            
        except Exception as e:
            print(f"保存节假日配置失败: {e}")
    
    def add_holiday(self, date_str: str) -> bool:
        """
        添加节假日
        
        Args:
            date_str: 日期字符串 "YYYY-MM-DD"
            
        Returns:
            bool: 是否添加成功
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year
            
            if year not in self.holidays:
                self.holidays[year] = set()
            
            self.holidays[year].add(date_str)
            
            # 如果该日期在调休工作日中，则移除
            if year in self.workdays:
                self.workdays[year].discard(date_str)
            
            print(f"已添加节假日: {date_str}")
            return True
            
        except ValueError:
            print(f"无效的日期格式: {date_str}")
            return False
    
    def add_workday(self, date_str: str) -> bool:
        """
        添加调休工作日
        
        Args:
            date_str: 日期字符串 "YYYY-MM-DD"
            
        Returns:
            bool: 是否添加成功
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year
            
            if year not in self.workdays:
                self.workdays[year] = set()
            
            self.workdays[year].add(date_str)
            
            # 如果该日期在节假日中，则移除
            if year in self.holidays:
                self.holidays[year].discard(date_str)
            
            print(f"已添加调休工作日: {date_str}")
            return True
            
        except ValueError:
            print(f"无效的日期格式: {date_str}")
            return False
    
    def remove_holiday(self, date_str: str) -> bool:
        """
        移除节假日
        
        Args:
            date_str: 日期字符串 "YYYY-MM-DD"
            
        Returns:
            bool: 是否移除成功
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year
            
            if year in self.holidays and date_str in self.holidays[year]:
                self.holidays[year].remove(date_str)
                print(f"已移除节假日: {date_str}")
                return True
            else:
                print(f"节假日不存在: {date_str}")
                return False
                
        except ValueError:
            print(f"无效的日期格式: {date_str}")
            return False
    
    def remove_workday(self, date_str: str) -> bool:
        """
        移除调休工作日
        
        Args:
            date_str: 日期字符串 "YYYY-MM-DD"
            
        Returns:
            bool: 是否移除成功
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year
            
            if year in self.workdays and date_str in self.workdays[year]:
                self.workdays[year].remove(date_str)
                print(f"已移除调休工作日: {date_str}")
                return True
            else:
                print(f"调休工作日不存在: {date_str}")
                return False
                
        except ValueError:
            print(f"无效的日期格式: {date_str}")
            return False
    
    def is_holiday(self, date_str: str) -> bool:
        """
        判断是否为节假日
        
        Args:
            date_str: 日期字符串 "YYYY-MM-DD"
            
        Returns:
            bool: 是否为节假日
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year
            
            return year in self.holidays and date_str in self.holidays[year]
            
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
            
            return year in self.workdays and date_str in self.workdays[year]
            
        except ValueError:
            return False
    
    def get_holidays_by_year(self, year: int) -> List[str]:
        """
        获取指定年份的所有节假日
        
        Args:
            year: 年份
            
        Returns:
            List[str]: 节假日列表
        """
        if year in self.holidays:
            return sorted(list(self.holidays[year]))
        return []
    
    def get_workdays_by_year(self, year: int) -> List[str]:
        """
        获取指定年份的所有调休工作日
        
        Args:
            year: 年份
            
        Returns:
            List[str]: 调休工作日列表
        """
        if year in self.workdays:
            return sorted(list(self.workdays[year]))
        return []
    
    def get_available_years(self) -> List[int]:
        """
        获取所有可用的年份
        
        Returns:
            List[int]: 年份列表
        """
        all_years = set(self.holidays.keys()) | set(self.workdays.keys())
        return sorted(list(all_years))
    
    def add_batch_holidays(self, holidays: List[str]) -> int:
        """
        批量添加节假日
        
        Args:
            holidays: 节假日列表
            
        Returns:
            int: 成功添加的数量
        """
        success_count = 0
        for holiday in holidays:
            if self.add_holiday(holiday):
                success_count += 1
        return success_count
    
    def add_batch_workdays(self, workdays: List[str]) -> int:
        """
        批量添加调休工作日
        
        Args:
            workdays: 调休工作日列表
            
        Returns:
            int: 成功添加的数量
        """
        success_count = 0
        for workday in workdays:
            if self.add_workday(workday):
                success_count += 1
        return success_count
    
    def clear_year(self, year: int):
        """
        清空指定年份的所有配置
        
        Args:
            year: 年份
        """
        if year in self.holidays:
            del self.holidays[year]
        
        if year in self.workdays:
            del self.workdays[year]
        
        print(f"已清空 {year} 年的节假日配置")
    
    def print_year_summary(self, year: int):
        """
        打印指定年份的节假日摘要
        
        Args:
            year: 年份
        """
        print(f"\n=== {year} 年节假日配置 ===")
        
        holidays = self.get_holidays_by_year(year)
        workdays = self.get_workdays_by_year(year)
        
        print(f"节假日 ({len(holidays)} 天):")
        for holiday in holidays:
            print(f"  {holiday}")
        
        print(f"\n调休工作日 ({len(workdays)} 天):")
        for workday in workdays:
            print(f"  {workday}")
        
        print("=" * 30)


def main():
    """命令行工具主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="节假日管理工具")
    parser.add_argument("--config", default="config/holidays.json", help="配置文件路径")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 添加节假日
    add_holiday_parser = subparsers.add_parser("add-holiday", help="添加节假日")
    add_holiday_parser.add_argument("date", help="日期 (YYYY-MM-DD)")
    
    # 添加调休工作日
    add_workday_parser = subparsers.add_parser("add-workday", help="添加调休工作日")
    add_workday_parser.add_argument("date", help="日期 (YYYY-MM-DD)")
    
    # 移除节假日
    remove_holiday_parser = subparsers.add_parser("remove-holiday", help="移除节假日")
    remove_holiday_parser.add_argument("date", help="日期 (YYYY-MM-DD)")
    
    # 移除调休工作日
    remove_workday_parser = subparsers.add_parser("remove-workday", help="移除调休工作日")
    remove_workday_parser.add_argument("date", help="日期 (YYYY-MM-DD)")
    
    # 查看年份摘要
    summary_parser = subparsers.add_parser("summary", help="查看年份摘要")
    summary_parser.add_argument("year", type=int, help="年份")
    
    # 列出所有年份
    list_parser = subparsers.add_parser("list-years", help="列出所有年份")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = HolidayManager(args.config)
    
    if args.command == "add-holiday":
        manager.add_holiday(args.date)
        manager.save_config()
    
    elif args.command == "add-workday":
        manager.add_workday(args.date)
        manager.save_config()
    
    elif args.command == "remove-holiday":
        manager.remove_holiday(args.date)
        manager.save_config()
    
    elif args.command == "remove-workday":
        manager.remove_workday(args.date)
        manager.save_config()
    
    elif args.command == "summary":
        manager.print_year_summary(args.year)
    
    elif args.command == "list-years":
        years = manager.get_available_years()
        print("可用年份:", ", ".join(map(str, years)))


if __name__ == "__main__":
    main()