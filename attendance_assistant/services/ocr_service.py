"""
OCR服务模块
负责文本识别和日期时间信息提取
"""
import logging
import re
from datetime import datetime
from typing import List, Dict, Optional
import numpy as np
import pytesseract
from PIL import Image
from paddleocr import PaddleOCR

logger = logging.getLogger(__name__)


class OCRService:
    """OCR服务类"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        # 初始化PaddleOCR实例
        self.ocr_engine = None
        self._initialize_ocr()
    
    def _initialize_ocr(self):
        """初始化OCR引擎"""
        try:
            self.ocr_engine = PaddleOCR(
                use_angle_cls=True,
                lang="ch",
                use_gpu=self.config.getboolean('OCR', 'use_gpu', fallback=False),
                ocr_version='PP-OCRv3',
                show_log=False  # 关闭详细日志输出
            )
            self.logger.info("OCR引擎初始化成功")
            
        except ImportError:
            self.logger.warning("PaddleOCR未安装，使用备用OCR方案")
            self.ocr_engine = None
        except Exception as e:
            self.logger.error(f"OCR引擎初始化失败: {str(e)}")
            # 不抛出异常，而是使用备用方案
            self.ocr_engine = None
    
    def recognize_text(self, image: np.ndarray) -> List[str]:
        """识别图像中的文本"""
        try:
            if self.ocr_engine is None:
                # 备用方案：使用Tesseract或其他OCR
                return self._fallback_ocr(image)
            
            # 使用PaddleOCR进行识别
            result = self.ocr_engine.ocr(image, cls=True)
            
            # 提取识别结果中的文本
            texts = []
            if result and result[0]:
                for line in result[0]:
                    if line and len(line) >= 2:
                        text = line[1][0]  # 提取文本内容
                        confidence = line[1][1]  # 置信度
                        if confidence > 0.5:  # 置信度阈值
                            texts.append(text)
            
            self.logger.info(f"识别到 {len(texts)} 个文本片段")
            return texts
            
        except Exception as e:
            self.logger.error(f"文本识别失败: {str(e)}")
            raise
    
    def _fallback_ocr(self, image: np.ndarray) -> List[str]:
        """备用OCR方案（当PaddleOCR不可用时）"""
        try:
            # 将numpy数组转换为PIL Image
            if len(image.shape) == 3:
                # BGR转RGB
                image_rgb = image[:, :, ::-1]
                pil_image = Image.fromarray(image_rgb)
            else:
                pil_image = Image.fromarray(image)
            # 使用Tesseract进行OCR识别
            # 配置中文识别
            custom_config = r'--oem 3 --psm 6 -l chi_sim+eng'
            text = pytesseract.image_to_string(pil_image, config=custom_config)
            
            # 将识别结果按行分割并过滤空行
            texts = [line.strip() for line in text.split('\n') if line.strip()]
            
            self.logger.info(f"Tesseract识别到 {len(texts)} 个文本片段")
            return texts
        except ImportError:
            self.logger.error("pytesseract未安装，无法使用Tesseract OCR")
            return []
        except Exception as e:
            self.logger.error(f"Tesseract OCR失败: {str(e)}")
            return []
    
    def extract_date_info(self, text_results: List[str]) -> Dict:
        """从OCR结果中提取日期信息"""
        date_info = {}
        
        # 匹配年月信息（如：2023年10月）
        year_month_pattern = r'(\d{4})年(\d{1,2})月'
        # 匹配日期（如：1日、15日）
        day_pattern = r'(\d{1,2})日'
        # 匹配星期（如：周一、星期二）
        weekday_pattern = r'周[一二三四五六日]|星期[一二三四五六日]'
        
        for text in text_results:
            # 尝试匹配年月
            year_month_match = re.search(year_month_pattern, text)
            if year_month_match:
                year = int(year_month_match.group(1))
                month = int(year_month_match.group(2))
                date_info['year'] = year
                date_info['month'] = month
                continue
            
            # 尝试匹配日期
            day_match = re.search(day_pattern, text)
            if day_match:
                day = int(day_match.group(1))
                date_info['day'] = day
                continue
            
            # 尝试匹配星期
            weekday_match = re.search(weekday_pattern, text)
            if weekday_match:
                weekday = weekday_match.group()
                date_info['weekday'] = weekday
                continue
        
        return date_info
    
    def extract_time_info(self, text_results: List[str]) -> Dict:
        """从OCR结果中提取时间信息"""
        time_info = {}
        
        # 匹配时间格式（如：09:00、18:30）
        time_pattern = r'(\d{1,2}):(\d{2})'
        
        times = []
        for text in text_results:
            time_matches = re.findall(time_pattern, text)
            for hour, minute in time_matches:
                time_str = f"{int(hour):02d}:{minute}"
                times.append(time_str)
        
        # 假设第一个时间是上班时间，第二个是下班时间
        if len(times) >= 2:
            time_info['clock_in'] = times[0]
            time_info['clock_out'] = times[1]
        elif len(times) == 1:
            time_info['clock_in'] = times[0]
            time_info['clock_out'] = None
        else:
            time_info['clock_in'] = None
            time_info['clock_out'] = None
        
        return time_info
    
    def extract_attendance_status(self, text_results: List[str]) -> Dict:
        """从OCR结果中提取考勤状态信息"""
        status_info = {}
        
        # 匹配状态关键词
        normal_patterns = [r'正常', r'出勤', r'已打卡']
        abnormal_patterns = [r'异常', r'缺勤', r'未打卡', r'迟到', r'早退']
        
        normal_count = 0
        abnormal_count = 0
        
        for text in text_results:
            for pattern in normal_patterns:
                if re.search(pattern, text):
                    normal_count += 1
                    break
            
            for pattern in abnormal_patterns:
                if re.search(pattern, text):
                    abnormal_count += 1
                    break
        
        # 根据计数判断整体状态
        if normal_count > abnormal_count:
            status_info['overall_status'] = '正常'
        elif abnormal_count > normal_count:
            status_info['overall_status'] = '异常'
        else:
            status_info['overall_status'] = '未知'
        
        status_info['normal_count'] = normal_count
        status_info['abnormal_count'] = abnormal_count
        
        return status_info
