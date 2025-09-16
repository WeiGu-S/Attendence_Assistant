"""
数据导出模块
负责将考勤数据导出为各种格式（CSV、Excel等）
"""
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import json

from ..core.models import MonthlyAttendance, DailyAttendance

logger = logging.getLogger(__name__)


class DataExporter:
    """数据导出器类"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def export_to_excel(self, data: MonthlyAttendance, file_path: str) -> bool:
        """导出数据到Excel文件"""
        try:
            # 准备数据
            export_data = self._prepare_export_data(data)
            
            # 创建DataFrame
            df = pd.DataFrame(export_data)
            
            # 确保目录存在
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 使用ExcelWriter创建多个工作表
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # 主数据工作表
                df.to_excel(writer, sheet_name='考勤明细', index=False)
                
                # 统计信息工作表
                stats_df = self._create_statistics_dataframe(data)
                stats_df.to_excel(writer, sheet_name='统计信息', index=False)
                
                # 异常记录工作表
                abnormal_df = self._create_abnormal_records_dataframe(data)
                if not abnormal_df.empty:
                    abnormal_df.to_excel(writer, sheet_name='异常记录', index=False)
            
            self.logger.info(f"Excel文件导出成功: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Excel导出失败: {str(e)}")
            return False
    
    def export_to_csv(self, data: MonthlyAttendance, file_path: str) -> bool:
        """导出数据到CSV文件"""
        try:
            # 准备数据
            export_data = self._prepare_export_data(data)
            
            # 创建DataFrame
            df = pd.DataFrame(export_data)
            
            # 确保目录存在
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 导出CSV
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            
            self.logger.info(f"CSV文件导出成功: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"CSV导出失败: {str(e)}")
            return False
    
    def export_to_json(self, data: MonthlyAttendance, file_path: str) -> bool:
        """导出数据到JSON文件"""
        try:
            # 确保目录存在
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 转换为字典并导出
            data_dict = data.to_dict()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"JSON文件导出成功: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"JSON导出失败: {str(e)}")
            return False
    
    def _prepare_export_data(self, data: MonthlyAttendance) -> List[Dict]:
        """准备导出数据"""
        export_data = []
        
        for day in data.data:
            row = {
                '日期': day.date,
                '星期': day.day_of_week,
                '类型': day.day_type,
                '上班时间': day.clock_in.time if day.clock_in.time else '',
                '上班状态': day.clock_in.status,
                '下班时间': day.clock_out.time if day.clock_out.time else '',
                '下班状态': day.clock_out.status,
                '是否确认': '是' if day.is_confirmed else '否',
                '备注': self._generate_remarks(day)
            }
            export_data.append(row)
        
        return export_data
    
    def _generate_remarks(self, day: DailyAttendance) -> str:
        """生成备注信息"""
        remarks = []
        
        if day.clock_in.status == '异常':
            remarks.append('上班异常')
        if day.clock_out.status == '异常':
            remarks.append('下班异常')
        if not day.is_confirmed and (day.clock_in.status == '异常' or day.clock_out.status == '异常'):
            remarks.append('待确认')
        
        return '; '.join(remarks)
    
    def _create_statistics_dataframe(self, data: MonthlyAttendance) -> pd.DataFrame:
        """创建统计信息DataFrame"""
        stats = data.statistics
        
        stats_data = [
            {'统计项目': '总天数', '数值': stats.get('total_days', 0)},
            {'统计项目': '工作日', '数值': stats.get('work_days', 0)},
            {'统计项目': '休息日', '数值': stats.get('rest_days', 0)},
            {'统计项目': '节假日', '数值': stats.get('holiday_days', 0)},
            {'统计项目': '正常上班打卡', '数值': stats.get('normal_clock_in', 0)},
            {'统计项目': '异常上班打卡', '数值': stats.get('abnormal_clock_in', 0)},
            {'统计项目': '正常下班打卡', '数值': stats.get('normal_clock_out', 0)},
            {'统计项目': '异常下班打卡', '数值': stats.get('abnormal_clock_out', 0)},
            {'统计项目': '已确认天数', '数值': stats.get('confirmed_days', 0)},
        ]
        
        # 计算出勤率
        work_days = stats.get('work_days', 0)
        normal_days = sum(1 for day in data.data 
                         if day.day_type == '工作日' and 
                         day.clock_in.status == '正常' and 
                         day.clock_out.status == '正常')
        
        if work_days > 0:
            attendance_rate = (normal_days / work_days) * 100
            stats_data.append({'统计项目': '出勤率(%)', '数值': f"{attendance_rate:.1f}"})
        
        return pd.DataFrame(stats_data)
    
    def _create_abnormal_records_dataframe(self, data: MonthlyAttendance) -> pd.DataFrame:
        """创建异常记录DataFrame"""
        abnormal_records = []
        
        for day in data.data:
            if day.clock_in.status == '异常' or day.clock_out.status == '异常':
                record = {
                    '日期': day.date,
                    '星期': day.day_of_week,
                    '异常类型': [],
                    '上班时间': day.clock_in.time if day.clock_in.time else '',
                    '下班时间': day.clock_out.time if day.clock_out.time else '',
                    '是否确认': '是' if day.is_confirmed else '否'
                }
                
                if day.clock_in.status == '异常':
                    record['异常类型'].append('上班异常')
                if day.clock_out.status == '异常':
                    record['异常类型'].append('下班异常')
                
                record['异常类型'] = '; '.join(record['异常类型'])
                abnormal_records.append(record)
        
        return pd.DataFrame(abnormal_records)
    
    def generate_report_summary(self, data: MonthlyAttendance) -> str:
        """生成报告摘要"""
        stats = data.statistics
        
        summary = f"""
考勤报告摘要 - {data.year_month}

基本统计:
- 总天数: {stats.get('total_days', 0)} 天
- 工作日: {stats.get('work_days', 0)} 天
- 休息日: {stats.get('rest_days', 0)} 天
- 节假日: {stats.get('holiday_days', 0)} 天

打卡统计:
- 正常上班打卡: {stats.get('normal_clock_in', 0)} 次
- 异常上班打卡: {stats.get('abnormal_clock_in', 0)} 次
- 正常下班打卡: {stats.get('normal_clock_out', 0)} 次
- 异常下班打卡: {stats.get('abnormal_clock_out', 0)} 次

确认状态:
- 已确认天数: {stats.get('confirmed_days', 0)} 天
- 待确认天数: {stats.get('total_days', 0) - stats.get('confirmed_days', 0)} 天

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        return summary