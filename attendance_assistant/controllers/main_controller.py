"""
主控制器模块
负责协调各个模块，处理业务逻辑
"""
import logging
import os
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import calendar
import re

from ..core.config_manager import ConfigManager
from ..services.image_processor import ImageProcessor, CellInfo, DotInfo
from ..services.ocr_service import OCRService
from ..services.data_exporter import DataExporter
from ..core.models import MonthlyAttendance, DailyAttendance, ClockRecord

logger = logging.getLogger(__name__)


class MainController:
    """主控制器类"""
    
    def __init__(self, view=None):
        self.view = view
        self.config = ConfigManager()
        self.image_processor = ImageProcessor(self.config)
        self.ocr_service = OCRService(self.config)
        self.data_exporter = DataExporter(self.config)
        self.current_data: Optional[MonthlyAttendance] = None
        self.logger = logging.getLogger(__name__)
    
    def process_uploaded_image(self, image_path: str) -> bool:
        """处理上传的图片完整流程"""
        try:
            self.logger.info(f"开始处理图片: {image_path}")
            
            # 1. 加载图像
            original_image = self.image_processor.load_image(image_path)
            
            # 2. 预处理
            processed_image = self.image_processor.preprocess_image(original_image)
            
            # 3. 检测表格单元格
            cells = self.image_processor.detect_table_cells(processed_image)
            
            if not cells:
                self.logger.warning("未检测到表格单元格")
                return False
            
            # 4. 提取文本和图案信息
            attendance_data = self._extract_attendance_data(original_image, cells)
            
            if not attendance_data:
                self.logger.warning("未能提取到有效的考勤数据")
                return False
            
            # 4.5. 验证和清理数据
            cleaned_data = self._validate_and_clean_attendance_data(attendance_data)
            
            # 5. 构建数据模型
            self.current_data = self._build_monthly_attendance(cleaned_data)
            
            # 6. 更新视图
            if self.view:
                self.view.update_calendar_display(self.current_data)
                self.view.show_statistics(self.current_data.statistics)
            
            self.logger.info("图片处理完成")
            return True
            
        except Exception as e:
            self.logger.error(f"图片处理失败: {str(e)}")
            return False
    
    def _extract_attendance_data(self, original_image, cells: List[CellInfo]) -> Dict:
        """从单元格中提取考勤数据"""
        attendance_data = {
            'year_month': None,
            'daily_records': []
        }
        
        try:
            # 按行处理单元格
            rows = self._group_cells_by_row(cells)
            
            for row_idx, row_cells in enumerate(rows):
                for cell in row_cells:
                    # 提取单元格图像
                    cell_image = self.image_processor.extract_cell_image(original_image, cell)
                    
                    # OCR识别文本
                    texts = self.ocr_service.recognize_text(cell_image)
                    
                    # 检测圆点
                    dots = self.image_processor.detect_dots(cell_image)
                    
                    # 解析单元格内容
                    cell_data = self._parse_cell_content(texts, dots, row_idx, cell.col)
                    
                    if cell_data:
                        if cell_data.get('type') == 'header' and cell_data.get('year_month'):
                            attendance_data['year_month'] = cell_data['year_month']
                        elif cell_data.get('type') == 'daily':
                            attendance_data['daily_records'].append(cell_data)
            return attendance_data
            
        except Exception as e:
            self.logger.error(f"考勤数据提取失败: {str(e)}")
            return {}
    
    def _group_cells_by_row(self, cells: List[CellInfo]) -> List[List[CellInfo]]:
        """按行分组单元格"""
        rows = {}
        for cell in cells:
            if cell.row not in rows:
                rows[cell.row] = []
            rows[cell.row].append(cell)
        
        # 按行号排序，每行内按列号排序
        sorted_rows = []
        for row_idx in sorted(rows.keys()):
            row_cells = sorted(rows[row_idx], key=lambda c: c.col)
            sorted_rows.append(row_cells)
        
        return sorted_rows
    
    def _parse_cell_content(self, texts: List[str], dots: List[DotInfo], 
                          row: int, col: int) -> Optional[Dict]:
        """解析单元格内容"""
        try:
            # 合并所有文本
            combined_text = ' '.join(texts)
            
            # 检查是否是标题行（包含年月信息）
            year_month_match = re.search(r'(\d{4})年(\d{1,2})月', combined_text)
            if year_month_match:
                year = int(year_month_match.group(1))
                month = int(year_month_match.group(2))
                return {
                    'type': 'header',
                    'year_month': f"{year:04d}-{month:02d}"
                }
            
            # 检查是否包含日期信息
            date_match = re.search(r'(\d{1,2})日?', combined_text)
            if date_match:
                day = int(date_match.group(1))
                
                # 提取星期信息
                weekday = self._extract_weekday(combined_text)
                
                # 提取时间信息
                times = self._extract_times(combined_text)
                
                # 根据圆点确定状态
                status = self._determine_status_from_dots(dots)
                
                return {
                    'type': 'daily',
                    'day': day,
                    'weekday': weekday,
                    'times': times,
                    'status': status,
                    'row': row,
                    'col': col
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"单元格内容解析失败: {str(e)}")
            return None
    
    def _extract_weekday(self, text: str) -> str:
        """提取星期信息"""
        weekday_patterns = {
            r'周日|星期日|周天|星期天': '周日',
            r'周一|星期一': '周一',
            r'周二|星期二': '周二', 
            r'周三|星期三': '周三',
            r'周四|星期四': '周四',
            r'周五|星期五': '周五',
            r'周六|星期六': '周六',
            r'周日|星期日|周天|星期天': '周日'
        }
        
        for pattern, weekday in weekday_patterns.items():
            if re.search(pattern, text):
                return weekday
        
        return ''
    
    def _extract_times(self, text: str) -> Dict[str, str]:
        """提取时间信息"""
        time_pattern = r'(\d{1,2}):(\d{2})'
        matches = re.findall(time_pattern, text)
        
        times = {}
        if len(matches) >= 2:
            times['clock_in'] = f"{int(matches[0][0]):02d}:{matches[0][1]}"
            times['clock_out'] = f"{int(matches[1][0]):02d}:{matches[1][1]}"
        elif len(matches) == 1:
            times['clock_in'] = f"{int(matches[0][0]):02d}:{matches[0][1]}"
            times['clock_out'] = ''
        else:
            times['clock_in'] = ''
            times['clock_out'] = ''
        
        return times
    
    def _determine_status_from_dots(self, dots: List[DotInfo]) -> Dict[str, str]:
        """根据圆点确定状态"""
        status = {
            'clock_in_status': '未打卡',
            'clock_out_status': '未打卡'
        }
        
        green_dots = [dot for dot in dots if dot.color == 'green']
        gray_dots = [dot for dot in dots if dot.color == 'gray']
        
        # 简单逻辑：绿色表示正常，灰色表示异常
        if len(green_dots) >= 2:
            status['clock_in_status'] = '正常'
            status['clock_out_status'] = '正常'
        elif len(green_dots) == 1:
            status['clock_in_status'] = '正常'
            if len(gray_dots) >= 1:
                status['clock_out_status'] = '异常'
        elif len(gray_dots) >= 1:
            status['clock_in_status'] = '异常'
            if len(gray_dots) >= 2:
                status['clock_out_status'] = '异常'
        
        return status
    
    def _validate_and_clean_attendance_data(self, attendance_data: Dict) -> Dict:
        """验证和清理考勤数据"""
        try:
            cleaned_data = {
                'year_month': attendance_data.get('year_month'),
                'daily_records': []
            }
            
            daily_records = attendance_data.get('daily_records', [])
            
            for record in daily_records:
                # 验证必要字段
                if not isinstance(record.get('day'), int):
                    continue
                
                day = record['day']
                if day < 1 or day > 31:
                    continue
                
                # 清理时间格式
                times = record.get('times', {})
                cleaned_times = {}
                
                for time_type in ['clock_in', 'clock_out']:
                    time_str = times.get(time_type, '').strip()
                    if time_str and ':' in time_str:
                        # 验证时间格式
                        try:
                            parts = time_str.split(':')
                            if len(parts) == 2:
                                hour = int(parts[0])
                                minute = int(parts[1])
                                if 0 <= hour <= 23 and 0 <= minute <= 59:
                                    cleaned_times[time_type] = f"{hour:02d}:{minute:02d}"
                                else:
                                    cleaned_times[time_type] = ''
                            else:
                                cleaned_times[time_type] = ''
                        except (ValueError, IndexError):
                            cleaned_times[time_type] = ''
                    else:
                        cleaned_times[time_type] = ''
                
                # 清理状态信息
                status = record.get('status', {})
                cleaned_status = {}
                
                for status_type in ['clock_in_status', 'clock_out_status']:
                    status_str = status.get(status_type, '未打卡')
                    if status_str in ['正常', '异常', '未打卡']:
                        cleaned_status[status_type] = status_str
                    else:
                        # 根据时间推断状态
                        time_key = status_type.replace('_status', '')
                        if cleaned_times.get(time_key):
                            cleaned_status[status_type] = '正常'
                        else:
                            cleaned_status[status_type] = '未打卡'
                
                # 添加清理后的记录
                cleaned_record = {
                    'type': 'daily',
                    'day': day,
                    'weekday': record.get('weekday', ''),
                    'times': cleaned_times,
                    'status': cleaned_status,
                    'row': record.get('row', 0),
                    'col': record.get('col', 0)
                }
                
                cleaned_data['daily_records'].append(cleaned_record)
            
            self.logger.info(f"数据清理完成，有效记录数: {len(cleaned_data['daily_records'])}")
            return cleaned_data
            
        except Exception as e:
            self.logger.error(f"数据清理失败: {str(e)}")
            return attendance_data
    
    def _build_monthly_attendance(self, attendance_data: Dict) -> MonthlyAttendance:
        """构建月度考勤数据模型"""
        try:
            # 获取年月信息
            year_month = attendance_data.get('year_month')
            daily_records_data = attendance_data.get('daily_records', [])
            
            # 如果没有年月信息，尝试从数据中推断或使用当前年月
            if not year_month:
                # 尝试从日期数据推断年月
                if daily_records_data:
                    # 假设是当前年份，根据数据中的最大日期推断月份
                    max_day = max(record.get('day', 0) for record in daily_records_data)
                    current_year = datetime.now().year
                    
                    # 简单推断：如果最大日期大于28，可能是30或31天的月份
                    if max_day == 31:
                        # 可能是1,3,5,7,8,10,12月，这里默认使用当前月份
                        current_month = datetime.now().month
                    elif max_day == 30:
                        # 可能是4,6,9,11月
                        current_month = datetime.now().month
                    elif max_day <= 29:
                        # 可能是2月或其他月份
                        current_month = datetime.now().month
                    else:
                        current_month = datetime.now().month
                    
                    year_month = f"{current_year:04d}-{current_month:02d}"
                else:
                    # 使用当前年月
                    now = datetime.now()
                    year_month = f"{now.year:04d}-{now.month:02d}"
            
            # 解析年月
            year, month = map(int, year_month.split('-'))
            
            # 获取该月的天数
            days_in_month = calendar.monthrange(year, month)[1]
            
            # 创建日期数据映射
            daily_data_map = {}
            for record in daily_records_data:
                day = record.get('day')
                if day and 1 <= day <= days_in_month:
                    daily_data_map[day] = record
            
            # 创建每日考勤记录
            daily_records = []
            
            for day in range(1, days_in_month + 1):
                date_str = f"{year:04d}-{month:02d}-{day:02d}"
                date_obj = datetime(year, month, day)
                weekday_num = date_obj.weekday()  # 0=Monday, 6=Sunday
                
                # 转换为中文星期 (Python的weekday: 0=Monday, 6=Sunday)
                weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
                weekday_str = weekdays[weekday_num]
                
                # 判断日期类型 (周一到周五为工作日，周六周日为休息日)
                day_type = '工作日' if weekday_num < 5 else '休息日'
                
                # 获取该日的数据
                day_data = daily_data_map.get(day, {})
                
                # 提取时间和状态信息
                times = day_data.get('times', {})
                status = day_data.get('status', {})
                
                # 处理时间格式
                clock_in_time = times.get('clock_in', '').strip()
                clock_out_time = times.get('clock_out', '').strip()
                
                # 处理状态信息
                clock_in_status = status.get('clock_in_status', '未打卡')
                clock_out_status = status.get('clock_out_status', '未打卡')
                
                # 如果有时间但状态为空，设置为正常
                if clock_in_time and clock_in_status == '未打卡':
                    clock_in_status = '正常'
                if clock_out_time and clock_out_status == '未打卡':
                    clock_out_status = '正常'
                
                # 创建打卡记录
                clock_in = ClockRecord(
                    time=clock_in_time,
                    status=clock_in_status
                )
                
                clock_out = ClockRecord(
                    time=clock_out_time,
                    status=clock_out_status
                )
                
                # 创建每日考勤记录
                daily_attendance = DailyAttendance(
                    date=date_str,
                    day_of_week=weekday_str,
                    day_type=day_type,
                    clock_in=clock_in,
                    clock_out=clock_out,
                    is_confirmed=False
                )
                
                daily_records.append(daily_attendance)
            
            # 创建月度考勤数据
            monthly_attendance = MonthlyAttendance(
                year_month=year_month,
                data=daily_records
            )
            
            self.logger.info(f"构建月度考勤数据完成: {year_month}, 共{len(daily_records)}天")
            self.logger.info(f"有效考勤记录: {len([r for r in daily_records if r.clock_in.time or r.clock_out.time])}天")
            
            return monthly_attendance
            
        except Exception as e:
            self.logger.error(f"构建月度考勤数据失败: {str(e)}")
            # 打印更详细的错误信息用于调试
            import traceback
            self.logger.error(f"详细错误信息: {traceback.format_exc()}")
            raise
    
    def export_to_excel(self, file_path: str) -> bool:
        """导出数据到Excel"""
        if not self.current_data:
            self.logger.warning("没有可导出的数据")
            return False
        
        return self.data_exporter.export_to_excel(self.current_data, file_path)
    
    def export_to_csv(self, file_path: str) -> bool:
        """导出数据到CSV"""
        if not self.current_data:
            self.logger.warning("没有可导出的数据")
            return False
        
        return self.data_exporter.export_to_csv(self.current_data, file_path)
    
    def update_attendance_record(self, date: str, field: str, value: str) -> bool:
        """更新考勤记录"""
        if not self.current_data:
            return False
        
        try:
            day = self.current_data.get_day(date)
            
            if field == 'clock_in_time':
                day.clock_in.time = value
            elif field == 'clock_out_time':
                day.clock_out.time = value
            elif field == 'clock_in_status':
                day.clock_in.status = value
            elif field == 'clock_out_status':
                day.clock_out.status = value
            elif field == 'day_type':
                day.day_type = value
            
            # 更新数据并重新计算统计
            self.current_data.update_day(date, day)
            
            # 更新视图
            if self.view:
                self.view.update_calendar_display(self.current_data)
                self.view.show_statistics(self.current_data.statistics)
            
            return True
            
        except Exception as e:
            self.logger.error(f"更新考勤记录失败: {str(e)}")
            return False
    
    def confirm_attendance(self, date: str) -> bool:
        """确认考勤记录"""
        if not self.current_data:
            return False
        
        try:
            day = self.current_data.get_day(date)
            day.is_confirmed = True
            
            # 更新数据
            self.current_data.update_day(date, day)
            
            # 更新视图
            if self.view:
                self.view.update_calendar_display(self.current_data)
                self.view.show_statistics(self.current_data.statistics)
            
            return True
            
        except Exception as e:
            self.logger.error(f"确认考勤记录失败: {str(e)}")
            return False
    
    def get_current_data(self) -> Optional[MonthlyAttendance]:
        """获取当前数据"""
        return self.current_data
    
    def process_raw_attendance_data(self, raw_data: Dict) -> bool:
        """处理原始考勤数据（用于测试和调试）"""
        try:
            self.logger.info("开始处理原始考勤数据")
            
            # 验证和清理数据
            cleaned_data = self._validate_and_clean_attendance_data(raw_data)
            
            # 构建数据模型
            self.current_data = self._build_monthly_attendance(cleaned_data)
            
            # 更新视图
            if self.view:
                self.view.update_calendar_display(self.current_data)
                self.view.show_statistics(self.current_data.statistics)
            
            self.logger.info("原始数据处理完成")
            return True
            
        except Exception as e:
            self.logger.error(f"原始数据处理失败: {str(e)}")
            return False
    
    def generate_report_summary(self) -> str:
        """生成报告摘要"""
        if not self.current_data:
            return "暂无数据"
        
        return self.data_exporter.generate_report_summary(self.current_data)