"""
配置管理模块
负责应用程序配置的读取、写入和管理
"""
import configparser
import os
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器类"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.logger = logging.getLogger(__name__)
        
        # 创建默认配置
        self._create_default_config()
        
        # 加载配置文件
        self._load_config()
    
    def _create_default_config(self):
        """创建默认配置"""
        # OCR配置
        self.config.add_section('OCR')
        self.config.set('OCR', 'use_gpu', 'False')
        self.config.set('OCR', 'model_path', './models')
        self.config.set('OCR', 'confidence_threshold', '0.5')
        
        # UI配置
        self.config.add_section('UI')
        self.config.set('UI', 'language', 'zh_CN')
        self.config.set('UI', 'theme', 'light')
        self.config.set('UI', 'window_width', '1200')
        self.config.set('UI', 'window_height', '800')
        
        # 导出配置
        self.config.add_section('Export')
        self.config.set('Export', 'default_format', 'excel')
        self.config.set('Export', 'default_path', './exports')
        
        # 图像处理配置
        self.config.add_section('ImageProcessing')
        self.config.set('ImageProcessing', 'min_cell_area', '100')
        self.config.set('ImageProcessing', 'min_dot_area', '10')
        self.config.set('ImageProcessing', 'circularity_threshold', '0.7')
        
        # 日志配置
        self.config.add_section('Logging')
        self.config.set('Logging', 'level', 'INFO')
        self.config.set('Logging', 'file_path', 'app.log')
        self.config.set('Logging', 'max_file_size', '10485760')  # 10MB
        self.config.set('Logging', 'backup_count', '5')
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                self.config.read(self.config_file, encoding='utf-8')
                self.logger.info(f"配置文件加载成功: {self.config_file}")
            else:
                # 如果配置文件不存在，创建默认配置文件
                self.save_config()
                self.logger.info(f"创建默认配置文件: {self.config_file}")
        except Exception as e:
            self.logger.error(f"配置文件加载失败: {str(e)}")
            raise
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            self.logger.info(f"配置文件保存成功: {self.config_file}")
        except Exception as e:
            self.logger.error(f"配置文件保存失败: {str(e)}")
            raise
    
    def get(self, section: str, option: str, fallback: Any = None) -> str:
        """获取配置值"""
        try:
            return self.config.get(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def getint(self, section: str, option: str, fallback: int = 0) -> int:
        """获取整数配置值"""
        try:
            return self.config.getint(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def getfloat(self, section: str, option: str, fallback: float = 0.0) -> float:
        """获取浮点数配置值"""
        try:
            return self.config.getfloat(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def getboolean(self, section: str, option: str, fallback: bool = False) -> bool:
        """获取布尔配置值"""
        try:
            return self.config.getboolean(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def set(self, section: str, option: str, value: str):
        """设置配置值"""
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            self.config.set(section, option, str(value))
        except Exception as e:
            self.logger.error(f"设置配置失败: {str(e)}")
            raise
    
    def get_section(self, section: str) -> Dict[str, str]:
        """获取整个配置节"""
        try:
            if self.config.has_section(section):
                return dict(self.config.items(section))
            else:
                return {}
        except Exception as e:
            self.logger.error(f"获取配置节失败: {str(e)}")
            return {}
    
    def ensure_directory(self, path: str):
        """确保目录存在"""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.error(f"创建目录失败: {str(e)}")
            raise