"""
主窗口模块
应用程序的主界面
"""
import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QMessageBox, 
                            QSplitter, QTextEdit, QGroupBox, QGridLayout,
                            QProgressBar, QStatusBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from ..controllers.main_controller import MainController
from ..core.models import MonthlyAttendance
from .attendance_calendar import AttendanceCalendar
from .control_panel import ControlPanel


class ImageProcessingThread(QThread):
    """图像处理线程"""
    finished = pyqtSignal(bool)
    progress = pyqtSignal(str)
    
    def __init__(self, controller, image_path):
        super().__init__()
        self.controller = controller
        self.image_path = image_path
    
    def run(self):
        try:
            self.progress.emit("正在处理图像...")
            success = self.controller.process_uploaded_image(self.image_path)
            self.finished.emit(success)
        except Exception as e:
            self.progress.emit(f"处理失败: {str(e)}")
            self.finished.emit(False)


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        try:
            self.controller = MainController(self)
            self.processing_thread = None
            self._setup_ui()
            self._setup_connections()
        except Exception as e:
            print(f"主窗口初始化失败: {e}")
            import traceback
            traceback.print_exc()
            raise
        
    def _setup_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("考勤助手 - Attendance Assistant v1.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置应用图标（如果有的话）
        # self.setWindowIcon(QIcon('assets/icon.ico'))
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧控制面板
        self.control_panel = ControlPanel(self)
        splitter.addWidget(self.control_panel)
        
        # 右侧日历视图
        self.calendar_view = self._create_calendar_view()
        splitter.addWidget(self.calendar_view)
        
        # 设置分割器比例
        splitter.setSizes([300, 900])
        
        main_layout.addWidget(splitter)
        
        # 创建状态栏
        self._create_status_bar()
        
        # 设置样式
        self._apply_styles()
    
    def _create_calendar_view(self) -> QWidget:
        """创建日历视图"""
        calendar_widget = QWidget()
        layout = QVBoxLayout(calendar_widget)
        
        # 标题
        title_label = QLabel("考勤日历")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 考勤日历
        self.attendance_calendar = AttendanceCalendar()
        layout.addWidget(self.attendance_calendar)
        
        # 图例
        legend_widget = self._create_legend()
        layout.addWidget(legend_widget)
        
        return calendar_widget
    
    def _create_legend(self) -> QWidget:
        """创建图例"""
        legend_group = QGroupBox("状态图例")
        layout = QGridLayout(legend_group)
        
        # 状态说明
        legends = [
            ("正常", "#4CAF50", "绿色表示正常打卡"),
            ("异常", "#FF9800", "橙色表示异常打卡"),
            ("未打卡", "#F44336", "红色表示未打卡"),
            ("休息日", "#E0E0E0", "灰色表示休息日"),
            ("已确认", "#2196F3", "蓝色边框表示已确认")
        ]
        
        for i, (status, color, description) in enumerate(legends):
            # 颜色块
            color_label = QLabel()
            color_label.setStyleSheet(f"background-color: {color}; border: 1px solid #ccc;")
            color_label.setFixedSize(20, 20)
            
            # 说明文字
            desc_label = QLabel(f"{status}: {description}")
            
            layout.addWidget(color_label, i, 0)
            layout.addWidget(desc_label, i, 1)
        
        return legend_group
    
    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
    
    def _setup_connections(self):
        """设置信号连接"""
        try:
            # 控制面板信号
            if hasattr(self.control_panel, 'image_upload_requested'):
                self.control_panel.image_upload_requested.connect(self.upload_image)
            if hasattr(self.control_panel, 'export_requested'):
                self.control_panel.export_requested.connect(self.export_data)
            if hasattr(self.control_panel, 'data_update_requested'):
                self.control_panel.data_update_requested.connect(self.update_data)
            
            # 日历视图信号
            if hasattr(self.attendance_calendar, 'cell_clicked'):
                self.attendance_calendar.cell_clicked.connect(self.on_calendar_cell_clicked)
        except Exception as e:
            print(f"信号连接失败: {e}")
            # 不抛出异常，继续运行
    
    def _apply_styles(self):
        """应用样式"""
        style = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 5px;
            margin-top: 1ex;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #1976D2;
        }
        
        QPushButton:pressed {
            background-color: #0D47A1;
        }
        
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
        """
        self.setStyleSheet(style)
    
    def upload_image(self):
        """上传图片"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "选择考勤图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if file_path:
            self._process_image(file_path)
    
    def _process_image(self, image_path: str):
        """处理图片"""
        try:
            # 基本验证
            if not os.path.exists(image_path):
                QMessageBox.warning(self, "错误", "选择的图片文件不存在！")
                return
            
            # 检查文件大小
            file_size = os.path.getsize(image_path)
            if file_size == 0:
                QMessageBox.warning(self, "错误", "选择的图片文件为空！")
                return
            
            # 检查文件扩展名
            valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']
            file_ext = os.path.splitext(image_path)[1].lower()
            if file_ext not in valid_extensions:
                QMessageBox.warning(self, "错误", f"不支持的图片格式: {file_ext}")
                return
            
            # 显示进度
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 不确定进度
            self.status_label.setText("正在处理图片...")
            
            # 禁用相关按钮
            self.control_panel.set_processing_state(True)
            
            # 创建处理线程
            self.processing_thread = ImageProcessingThread(self.controller, image_path)
            self.processing_thread.finished.connect(self._on_processing_finished)
            self.processing_thread.progress.connect(self._on_processing_progress)
            self.processing_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理图片时发生错误: {str(e)}")
            self.progress_bar.setVisible(False)
            self.control_panel.set_processing_state(False)
    
    def _on_processing_finished(self, success: bool):
        """处理完成回调"""
        # 隐藏进度
        self.progress_bar.setVisible(False)
        
        # 恢复按钮状态
        self.control_panel.set_processing_state(False)
        
        if success:
            self.status_label.setText("图片处理完成")
            QMessageBox.information(self, "成功", "图片处理完成！考勤数据已加载到日历中。")
            # 更新界面显示
            if self.controller.current_data:
                self.update_calendar_display(self.controller.current_data)
                self.show_statistics(self.controller.current_data.statistics)
        else:
            self.status_label.setText("图片处理失败")
            QMessageBox.warning(self, "失败", 
                              "图片处理失败，可能的原因：\n"
                              "1. 图片格式不支持\n"
                              "2. 图片中没有检测到表格结构\n"
                              "3. OCR识别失败\n"
                              "请检查图片内容并重试。")
    
    def _on_processing_progress(self, message: str):
        """处理进度回调"""
        self.status_label.setText(message)
    
    def export_data(self, format_type: str, file_path: str):
        """导出数据"""
        if not self.controller.current_data:
            QMessageBox.warning(self, "警告", "没有可导出的数据，请先处理图片。")
            return
        
        try:
            success = False
            if format_type.lower() == 'excel':
                success = self.controller.export_to_excel(file_path)
            elif format_type.lower() == 'csv':
                success = self.controller.export_to_csv(file_path)
            
            if success:
                QMessageBox.information(self, "成功", f"数据已成功导出到: {file_path}")
                self.status_label.setText(f"数据已导出: {os.path.basename(file_path)}")
            else:
                QMessageBox.warning(self, "失败", "数据导出失败。")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出过程中发生错误: {str(e)}")
    
    def update_data(self, date: str, field: str, value: str):
        """更新数据"""
        success = self.controller.update_attendance_record(date, field, value)
        if success:
            self.status_label.setText(f"已更新 {date} 的数据")
        else:
            QMessageBox.warning(self, "失败", "数据更新失败。")
    
    def on_calendar_cell_clicked(self, date: str):
        """日历单元格点击事件"""
        if self.controller.current_data:
            try:
                day_data = self.controller.current_data.get_day(date)
                self.control_panel.show_day_details(day_data)
            except ValueError:
                pass  # 日期不存在，忽略
    
    def update_calendar_display(self, data: MonthlyAttendance):
        """更新日历显示"""
        self.attendance_calendar.set_attendance_data(data)
        self.control_panel.update_statistics(data.statistics)
    
    def show_statistics(self, stats: dict):
        """显示统计信息"""
        self.control_panel.update_statistics(stats)
    
    def closeEvent(self, event):
        """关闭事件"""
        # 如果有处理线程在运行，等待其完成
        if self.processing_thread and self.processing_thread.isRunning():
            reply = QMessageBox.question(
                self, 
                "确认退出", 
                "图片正在处理中，确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.processing_thread.terminate()
                self.processing_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()