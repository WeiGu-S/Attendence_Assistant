"""
考勤日历组件
自定义日历部件，显示考勤状态
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QDate
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QFontMetrics
from datetime import datetime, timedelta
import calendar

from ..core.models import MonthlyAttendance, DailyAttendance


class AttendanceCalendar(QWidget):
    """自定义考勤日历部件"""
    
    cell_clicked = pyqtSignal(str)  # 发送被点击的日期字符串
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.attendance_data = None
        self.current_year_month = None
        self.cell_width = 120
        self.cell_height = 80
        self.header_height = 40
        self.margin = 10
        
        # 颜色定义
        self.colors = {
            'normal': QColor(76, 175, 80),      # 绿色 - 正常
            'abnormal': QColor(255, 152, 0),    # 橙色 - 异常
            'absent': QColor(244, 67, 54),      # 红色 - 未打卡
            'rest': QColor(224, 224, 224),      # 灰色 - 休息日
            'confirmed': QColor(33, 150, 243),  # 蓝色 - 已确认边框
            'text': QColor(33, 33, 33),         # 深灰色 - 文字
            'border': QColor(200, 200, 200),    # 浅灰色 - 边框
            'background': QColor(255, 255, 255) # 白色 - 背景
        }
        
        self.setMinimumSize(800, 600)
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 月份导航
        nav_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("◀ 上月")
        self.next_button = QPushButton("下月 ▶")
        self.month_label = QLabel("请选择考勤图片")
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.month_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.month_label)
        nav_layout.addWidget(self.next_button)
        
        layout.addLayout(nav_layout)
        
        # 日历绘制区域
        self.calendar_widget = QWidget()
        self.calendar_widget.setMinimumHeight(500)
        layout.addWidget(self.calendar_widget)
        
        # 连接信号
        self.prev_button.clicked.connect(self._prev_month)
        self.next_button.clicked.connect(self._next_month)
        
        # 初始状态禁用导航按钮
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
    
    def set_attendance_data(self, data: MonthlyAttendance):
        """设置考勤数据并刷新显示"""
        self.attendance_data = data
        self.current_year_month = data.year_month
        
        # 更新月份标签
        year, month = map(int, data.year_month.split('-'))
        month_names = [
            "一月", "二月", "三月", "四月", "五月", "六月",
            "七月", "八月", "九月", "十月", "十一月", "十二月"
        ]
        self.month_label.setText(f"{year}年 {month_names[month-1]}")
        
        # 启用导航按钮
        self.prev_button.setEnabled(True)
        self.next_button.setEnabled(True)
        
        # 刷新显示
        self.update()
    
    def _prev_month(self):
        """切换到上月"""
        # 这里可以实现月份切换逻辑
        # 暂时只是示例，实际需要重新加载数据
        pass
    
    def _next_month(self):
        """切换到下月"""
        # 这里可以实现月份切换逻辑
        # 暂时只是示例，实际需要重新加载数据
        pass
    
    def paintEvent(self, event):
        """自定义绘制日历"""
        if not self.attendance_data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制日历
        self._draw_calendar(painter)
    
    def _draw_calendar(self, painter: QPainter):
        """绘制日历"""
        # 获取年月
        year, month = map(int, self.current_year_month.split('-'))
        
        # 获取该月第一天是星期几（0=Monday, 6=Sunday）
        first_day = datetime(year, month, 1)
        first_weekday = first_day.weekday()
        
        # 转换为以周日为起始的星期数（0=Sunday, 1=Monday, ..., 6=Saturday）
        # Python的weekday(): 0=Monday, 6=Sunday
        # 我们需要: 0=Sunday, 1=Monday, ..., 6=Saturday
        first_weekday_sunday_start = (first_weekday + 1) % 7
        
        # 获取该月天数
        days_in_month = calendar.monthrange(year, month)[1]
        
        # 绘制星期标题
        self._draw_weekday_headers(painter)
        
        # 计算起始位置
        start_x = self.margin
        start_y = self.margin + self.header_height*2
        
        # 绘制日期单元格
        for day in range(1, days_in_month + 1):
            # 计算位置（以周日为第一列）
            total_days = first_weekday_sunday_start + day - 1
            row = total_days // 7
            col = total_days % 7
            
            x = start_x + col * self.cell_width
            y = start_y + row * self.cell_height
            
            # 获取该日的考勤数据
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            day_data = self._get_day_data(date_str)
            
            # 绘制单元格
            self._draw_day_cell(painter, x, y, day, day_data)
    
    def _draw_weekday_headers(self, painter: QPainter):
        """绘制星期标题"""
        weekdays = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
        
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.setPen(QPen(self.colors['text']))
        
        for i, weekday in enumerate(weekdays):
            x = self.margin + i * self.cell_width
            y = self.margin + self.header_height
            rect = QRect(x, y, self.cell_width, self.header_height)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, weekday)
    
    def _draw_day_cell(self, painter: QPainter, x: int, y: int, day: int, day_data: DailyAttendance):
        """绘制日期单元格"""
        rect = QRect(x, y, self.cell_width, self.cell_height)
        
        # 确定背景颜色
        bg_color = self._get_cell_background_color(day_data)
        
        # 绘制背景
        painter.fillRect(rect, QBrush(bg_color))
        
        # 绘制边框
        border_color = self.colors['confirmed'] if day_data and day_data.is_confirmed else self.colors['border']
        border_width = 2 if day_data and day_data.is_confirmed else 1
        painter.setPen(QPen(border_color, border_width))
        painter.drawRect(rect)
        
        # 绘制日期数字
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.setPen(QPen(self.colors['text']))
        
        date_rect = QRect(x + 5, y + 5, self.cell_width - 10, 20)
        painter.drawText(date_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, str(day))
        
        # 绘制考勤信息
        if day_data:
            self._draw_attendance_info(painter, x, y, day_data)
    
    def _get_cell_background_color(self, day_data: DailyAttendance) -> QColor:
        """获取单元格背景颜色"""
        if not day_data:
            return self.colors['background']
        
        if day_data.day_type == '休息日' or day_data.day_type == '节假日':
            return self.colors['rest']
        
        # 检查打卡状态
        clock_in_normal = day_data.clock_in.status == '正常'
        clock_out_normal = day_data.clock_out.status == '正常'
        
        if clock_in_normal and clock_out_normal:
            return self.colors['normal']
        elif day_data.clock_in.status == '未打卡' and day_data.clock_out.status == '未打卡':
            return self.colors['absent']
        else:
            return self.colors['abnormal']
    
    def _draw_attendance_info(self, painter: QPainter, x: int, y: int, day_data: DailyAttendance):
        """绘制考勤信息"""
        painter.setFont(QFont("Arial", 8))
        painter.setPen(QPen(self.colors['text']))
        
        # 上班时间
        if day_data.clock_in.time:
            clock_in_rect = QRect(x + 5, y + 25, self.cell_width - 10, 15)
            clock_in_text = f"上: {day_data.clock_in.time}"
            painter.drawText(clock_in_rect, Qt.AlignmentFlag.AlignLeft, clock_in_text)
        
        # 下班时间
        if day_data.clock_out.time:
            clock_out_rect = QRect(x + 5, y + 40, self.cell_width - 10, 15)
            clock_out_text = f"下: {day_data.clock_out.time}"
            painter.drawText(clock_out_rect, Qt.AlignmentFlag.AlignLeft, clock_out_text)
        
        # 状态指示器
        self._draw_status_indicators(painter, x, y, day_data)
    
    def _draw_status_indicators(self, painter: QPainter, x: int, y: int, day_data: DailyAttendance):
        """绘制状态指示器（小圆点）"""
        # 上班状态指示器
        clock_in_color = self._get_status_color(day_data.clock_in.status)
        if clock_in_color:
            painter.setBrush(QBrush(clock_in_color))
            painter.setPen(QPen(clock_in_color))
            painter.drawEllipse(x + self.cell_width - 25, y + 25, 8, 8)
        
        # 下班状态指示器
        clock_out_color = self._get_status_color(day_data.clock_out.status)
        if clock_out_color:
            painter.setBrush(QBrush(clock_out_color))
            painter.setPen(QPen(clock_out_color))
            painter.drawEllipse(x + self.cell_width - 25, y + 40, 8, 8)
    
    def _get_status_color(self, status: str) -> QColor:
        """根据状态获取颜色"""
        if status == '正常':
            return self.colors['normal']
        elif status == '异常':
            return self.colors['abnormal']
        elif status == '未打卡':
            return self.colors['absent']
        else:
            return None
    
    def _get_day_data(self, date_str: str) -> DailyAttendance:
        """获取指定日期的数据"""
        if not self.attendance_data:
            return None
        
        for day in self.attendance_data.data:
            if day.date == date_str:
                return day
        
        return None
    
    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        if not self.attendance_data or event.button() != Qt.MouseButton.LeftButton:
            return
        
        # 计算点击的日期
        clicked_date = self._get_clicked_date(event.x(), event.y())
        if clicked_date:
            self.cell_clicked.emit(clicked_date)
    
    def _get_clicked_date(self, x: int, y: int) -> str:
        """根据点击位置计算日期"""
        # 检查是否在日历区域内
        if y < self.margin + self.header_height:
            return None
        
        # 计算行列
        col = (x - self.margin) // self.cell_width
        row = (y - self.margin - self.header_height) // self.cell_height
        
        if col < 0 or col >= 7 or row < 0:
            return None
        
        # 计算日期
        year, month = map(int, self.current_year_month.split('-'))
        first_day = datetime(year, month, 1)
        first_weekday = first_day.weekday()
        
        # 转换为以周日为起始的星期数
        first_weekday_sunday_start = (first_weekday + 1) % 7
        
        day = row * 7 + col - first_weekday_sunday_start + 1
        
        # 检查日期有效性
        days_in_month = calendar.monthrange(year, month)[1]
        if day < 1 or day > days_in_month:
            return None
        
        return f"{year:04d}-{month:02d}-{day:02d}"
    
    def sizeHint(self):
        """建议大小"""
        width = 7 * self.cell_width + 2 * self.margin
        height = 6 * self.cell_height + self.header_height + 2 * self.margin
        return self.size().__class__(width, height)