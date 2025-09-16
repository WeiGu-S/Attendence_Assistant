"""
简化版主窗口
用于调试和修复崩溃问题
"""
import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QMessageBox, 
                            QSplitter, QTextEdit, QGroupBox, QGridLayout,
                            QProgressBar, QStatusBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon


class SimpleMainWindow(QMainWindow):
    """简化版主窗口类"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        
    def _setup_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("考勤助手 - Attendance Assistant v1.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 添加标题
        title_label = QLabel("考勤助手")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        main_layout.addWidget(title_label)
        
        # 添加说明
        info_label = QLabel("程序已启动，上传图片功能正在开发中...")
        info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(info_label)
        
        # 添加上传按钮
        upload_button = QPushButton("上传考勤图片")
        upload_button.clicked.connect(self.upload_image)
        main_layout.addWidget(upload_button)
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
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
            try:
                # 基本验证
                if not os.path.exists(file_path):
                    QMessageBox.warning(self, "错误", "选择的图片文件不存在！")
                    return
                
                # 检查文件大小
                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    QMessageBox.warning(self, "错误", "选择的图片文件为空！")
                    return
                
                # 检查文件扩展名
                valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext not in valid_extensions:
                    QMessageBox.warning(self, "错误", f"不支持的图片格式: {file_ext}")
                    return
                
                # 显示成功信息
                file_name = os.path.basename(file_path)
                size_mb = file_size / (1024 * 1024)
                
                QMessageBox.information(
                    self, 
                    "图片上传成功", 
                    f"已成功选择图片:\n\n"
                    f"文件名: {file_name}\n"
                    f"大小: {size_mb:.2f} MB\n"
                    f"路径: {file_path}\n\n"
                    f"注意: 完整的OCR识别功能正在开发中，"
                    f"目前仅验证图片文件的有效性。"
                )
                
                self.status_bar.showMessage(f"已选择图片: {file_name} ({size_mb:.2f} MB)")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"处理图片时发生错误: {str(e)}")
                self.status_bar.showMessage("图片处理失败")