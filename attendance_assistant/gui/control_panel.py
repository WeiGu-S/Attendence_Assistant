"""
控制面板组件
包含文件上传、数据导出、统计信息等功能
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QGroupBox, QGridLayout, QTextEdit, 
                            QComboBox, QLineEdit, QFileDialog, QMessageBox,
                            QFormLayout, QSpinBox, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
import os

from ..core.models import DailyAttendance


class ControlPanel(QWidget):
    """控制面板类"""
    
    image_upload_requested = pyqtSignal()
    export_requested = pyqtSignal(str, str)  # format, file_path
    data_update_requested = pyqtSignal(str, str, str)  # date, field, value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_day_data = None
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 文件操作区域
        file_group = self._create_file_operations_group()
        layout.addWidget(file_group)
        
        # 统计信息区域
        stats_group = self._create_statistics_group()
        layout.addWidget(stats_group)
        
        # 数据编辑区域
        edit_group = self._create_data_edit_group()
        layout.addWidget(edit_group)
        
        # 导出操作区域
        export_group = self._create_export_group()
        layout.addWidget(export_group)
        
        # 添加弹性空间
        layout.addStretch()
    
    def _create_file_operations_group(self) -> QGroupBox:
        """创建文件操作组"""
        group = QGroupBox("文件操作")
        layout = QVBoxLayout(group)
        
        # 上传按钮
        self.upload_button = QPushButton("📁 选择考勤图片")
        self.upload_button.clicked.connect(self.image_upload_requested.emit)
        layout.addWidget(self.upload_button)
        
        # 文件信息显示
        self.file_info_label = QLabel("未选择文件")
        self.file_info_label.setWordWrap(True)
        self.file_info_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.file_info_label)
        
        return group
    
    def _create_statistics_group(self) -> QGroupBox:
        """创建统计信息组"""
        group = QGroupBox("统计信息")
        self.stats_layout = QGridLayout(group)
        
        # 初始化统计标签
        self.stats_labels = {}
        stats_items = [
            ("total_days", "总天数"),
            ("work_days", "工作日"),
            ("rest_days", "休息日"),
            ("normal_clock_in", "正常上班"),
            ("abnormal_clock_in", "异常上班"),
            ("normal_clock_out", "正常下班"),
            ("abnormal_clock_out", "异常下班"),
            ("confirmed_days", "已确认")
        ]
        
        for i, (key, label) in enumerate(stats_items):
            row = i // 2
            col = (i % 2) * 2
            
            label_widget = QLabel(f"{label}:")
            value_widget = QLabel("0")
            value_widget.setStyleSheet("font-weight: bold; color: #2196F3;")
            
            self.stats_layout.addWidget(label_widget, row, col)
            self.stats_layout.addWidget(value_widget, row, col + 1)
            
            self.stats_labels[key] = value_widget
        
        return group
    
    def _create_data_edit_group(self) -> QGroupBox:
        """创建数据编辑组"""
        group = QGroupBox("数据编辑")
        layout = QFormLayout(group)
        
        # 日期显示
        self.date_label = QLabel("未选择日期")
        self.date_label.setStyleSheet("font-weight: bold; color: #333;")
        layout.addRow("选中日期:", self.date_label)
        
        # 日期类型
        self.day_type_combo = QComboBox()
        self.day_type_combo.addItems(["工作日", "休息日", "节假日"])
        self.day_type_combo.currentTextChanged.connect(self._on_day_type_changed)
        layout.addRow("日期类型:", self.day_type_combo)
        
        # 上班时间
        self.clock_in_time_edit = QLineEdit()
        self.clock_in_time_edit.setPlaceholderText("HH:MM")
        self.clock_in_time_edit.textChanged.connect(self._on_clock_in_time_changed)
        layout.addRow("上班时间:", self.clock_in_time_edit)
        
        # 上班状态
        self.clock_in_status_combo = QComboBox()
        self.clock_in_status_combo.addItems(["正常", "异常", "未打卡"])
        self.clock_in_status_combo.currentTextChanged.connect(self._on_clock_in_status_changed)
        layout.addRow("上班状态:", self.clock_in_status_combo)
        
        # 下班时间
        self.clock_out_time_edit = QLineEdit()
        self.clock_out_time_edit.setPlaceholderText("HH:MM")
        self.clock_out_time_edit.textChanged.connect(self._on_clock_out_time_changed)
        layout.addRow("下班时间:", self.clock_out_time_edit)
        
        # 下班状态
        self.clock_out_status_combo = QComboBox()
        self.clock_out_status_combo.addItems(["正常", "异常", "未打卡"])
        self.clock_out_status_combo.currentTextChanged.connect(self._on_clock_out_status_changed)
        layout.addRow("下班状态:", self.clock_out_status_combo)
        
        # 确认状态
        self.confirmed_checkbox = QCheckBox("已确认")
        self.confirmed_checkbox.stateChanged.connect(self._on_confirmed_changed)
        layout.addRow("", self.confirmed_checkbox)
        
        # 初始状态禁用编辑控件
        self._set_edit_enabled(False)
        
        return group
    
    def _create_export_group(self) -> QGroupBox:
        """创建导出操作组"""
        group = QGroupBox("数据导出")
        layout = QVBoxLayout(group)
        
        # 导出格式选择
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("格式:"))
        
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["Excel", "CSV"])
        format_layout.addWidget(self.export_format_combo)
        
        layout.addLayout(format_layout)
        
        # 导出按钮
        self.export_button = QPushButton("📊 导出数据")
        self.export_button.clicked.connect(self._on_export_clicked)
        self.export_button.setEnabled(False)
        layout.addWidget(self.export_button)
        
        return group
    
    def _set_edit_enabled(self, enabled: bool):
        """设置编辑控件的启用状态"""
        self.day_type_combo.setEnabled(enabled)
        self.clock_in_time_edit.setEnabled(enabled)
        self.clock_in_status_combo.setEnabled(enabled)
        self.clock_out_time_edit.setEnabled(enabled)
        self.clock_out_status_combo.setEnabled(enabled)
        self.confirmed_checkbox.setEnabled(enabled)
    
    def show_day_details(self, day_data: DailyAttendance):
        """显示日期详情"""
        self.current_day_data = day_data
        
        # 更新显示
        self.date_label.setText(f"{day_data.date} ({day_data.day_of_week})")
        
        # 阻止信号触发
        self.day_type_combo.blockSignals(True)
        self.clock_in_time_edit.blockSignals(True)
        self.clock_in_status_combo.blockSignals(True)
        self.clock_out_time_edit.blockSignals(True)
        self.clock_out_status_combo.blockSignals(True)
        self.confirmed_checkbox.blockSignals(True)
        
        # 设置值
        self.day_type_combo.setCurrentText(day_data.day_type)
        self.clock_in_time_edit.setText(day_data.clock_in.time)
        self.clock_in_status_combo.setCurrentText(day_data.clock_in.status)
        self.clock_out_time_edit.setText(day_data.clock_out.time)
        self.clock_out_status_combo.setCurrentText(day_data.clock_out.status)
        self.confirmed_checkbox.setChecked(day_data.is_confirmed)
        
        # 恢复信号
        self.day_type_combo.blockSignals(False)
        self.clock_in_time_edit.blockSignals(False)
        self.clock_in_status_combo.blockSignals(False)
        self.clock_out_time_edit.blockSignals(False)
        self.clock_out_status_combo.blockSignals(False)
        self.confirmed_checkbox.blockSignals(False)
        
        # 启用编辑
        self._set_edit_enabled(True)
    
    def update_statistics(self, stats: dict):
        """更新统计信息"""
        for key, label in self.stats_labels.items():
            value = stats.get(key, 0)
            label.setText(str(value))
        
        # 启用导出按钮
        self.export_button.setEnabled(True)
    
    def set_processing_state(self, processing: bool):
        """设置处理状态"""
        self.upload_button.setEnabled(not processing)
        if processing:
            self.upload_button.setText("🔄 处理中...")
            self.file_info_label.setText("正在处理图片，请稍候...")
        else:
            self.upload_button.setText("📁 选择考勤图片")
    
    def _on_day_type_changed(self, value: str):
        """日期类型改变"""
        if self.current_day_data:
            self.data_update_requested.emit(self.current_day_data.date, "day_type", value)
    
    def _on_clock_in_time_changed(self, value: str):
        """上班时间改变"""
        if self.current_day_data:
            self.data_update_requested.emit(self.current_day_data.date, "clock_in_time", value)
    
    def _on_clock_in_status_changed(self, value: str):
        """上班状态改变"""
        if self.current_day_data:
            self.data_update_requested.emit(self.current_day_data.date, "clock_in_status", value)
    
    def _on_clock_out_time_changed(self, value: str):
        """下班时间改变"""
        if self.current_day_data:
            self.data_update_requested.emit(self.current_day_data.date, "clock_out_time", value)
    
    def _on_clock_out_status_changed(self, value: str):
        """下班状态改变"""
        if self.current_day_data:
            self.data_update_requested.emit(self.current_day_data.date, "clock_out_status", value)
    
    def _on_confirmed_changed(self, state: int):
        """确认状态改变"""
        if self.current_day_data:
            confirmed = state == Qt.CheckState.Checked
            # 这里可以发送确认信号，或者直接更新
            # 暂时通过data_update_requested处理
            pass
    
    def _on_export_clicked(self):
        """导出按钮点击"""
        format_type = self.export_format_combo.currentText().lower()
        
        # 选择保存路径
        if format_type == "excel":
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存Excel文件",
                f"考勤数据_{self._get_current_month()}.xlsx",
                "Excel文件 (*.xlsx)"
            )
        else:  # CSV
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存CSV文件", 
                f"考勤数据_{self._get_current_month()}.csv",
                "CSV文件 (*.csv)"
            )
        
        if file_path:
            self.export_requested.emit(format_type, file_path)
    
    def _get_current_month(self) -> str:
        """获取当前月份字符串"""
        if self.current_day_data:
            return self.current_day_data.date[:7]  # YYYY-MM
        else:
            from datetime import datetime
            return datetime.now().strftime("%Y-%m")