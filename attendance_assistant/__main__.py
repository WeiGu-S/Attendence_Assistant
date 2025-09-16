"""
考勤助手主程序入口
支持 python -m attendance_assistant 运行
"""
import sys
import logging
import logging.handlers
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from .core.config_manager import ConfigManager
from .gui.main_window import MainWindow


def setup_logging(config: ConfigManager):
    """设置日志系统"""
    log_level = config.get('Logging', 'level', 'INFO')
    log_file = config.get('Logging', 'file_path', 'logs/app.log')
    max_file_size = config.getint('Logging', 'max_file_size', 10485760)
    backup_count = config.getint('Logging', 'backup_count', 5)
    
    # 确保日志目录存在
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            ),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("日志系统初始化完成")


def setup_directories(config: ConfigManager):
    """设置必要的目录"""
    # 创建导出目录
    export_path = config.get('Export', 'default_path', './exports')
    config.ensure_directory(export_path)
    
    # 创建模型目录
    model_path = config.get('OCR', 'model_path', './models')
    config.ensure_directory(model_path)
    
    # 创建日志目录
    log_file = config.get('Logging', 'file_path', 'logs/app.log')
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(__name__)
    logger.info("目录结构初始化完成")


def load_styles(app: QApplication):
    """加载应用程序样式"""
    try:
        # 获取样式文件路径
        current_dir = Path(__file__).parent
        style_file = current_dir / "resources" / "styles.qss"
        
        if style_file.exists():
            with open(style_file, 'r', encoding='utf-8') as f:
                app.setStyleSheet(f.read())
            logger = logging.getLogger(__name__)
            logger.info("样式文件加载成功")
        else:
            print(f"样式文件不存在: {style_file}")
    except Exception as e:
        print(f"加载样式文件失败: {e}")


def main():
    """主函数"""
    # 设置Qt应用程序属性（必须在创建QApplication之前）
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("考勤助手")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("AttendanceAssistant")
    
    try:
        # 初始化配置
        config = ConfigManager()
        
        # 设置日志
        setup_logging(config)
        
        # 设置目录
        setup_directories(config)
        
        # 加载样式
        load_styles(app)
        
        logger = logging.getLogger(__name__)
        logger.info("考勤助手启动")
        
        # 创建主窗口（使用简化版避免崩溃）
        from .gui.simple_main_window import SimpleMainWindow
        main_window = SimpleMainWindow()
        main_window.show()
        
        # 运行应用程序
        exit_code = app.exec_()
        
        logger.info("考勤助手退出")
        return exit_code
        
    except Exception as e:
        # 如果日志系统还没初始化，直接打印错误
        if 'logger' not in locals():
            print(f"启动失败: {str(e)}")
        else:
            logger.error(f"启动失败: {str(e)}")
        return 1


if __name__ == "__main__":
    # 运行主程序
    sys.exit(main())