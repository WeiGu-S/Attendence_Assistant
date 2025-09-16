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

from ..utils.logger import Logger, performance_monitor


class OCRService:
    """OCR服务类"""
    
    def __init__(self, config):
        self.config = config
        self.logger = Logger.get_logger(__name__)
        # 初始化PaddleOCR实例
        self.ocr_engine = None
        self._initialize_ocr()
    
    @performance_monitor("OCR引擎初始化")
    def _initialize_ocr(self):
        """初始化OCR引擎"""
        try:
            # 临时禁用PaddleOCR以避免崩溃问题
            self.logger.info("暂时跳过PaddleOCR初始化，使用备用方案")
            self.ocr_engine = None
            
            # 原始的PaddleOCR初始化代码（暂时注释掉）
            """
            use_gpu = self.config.getboolean('OCR', 'use_gpu', fallback=False)
            self.logger.info(f"正在初始化OCR引擎 (GPU: {'启用' if use_gpu else '禁用'})")
            
            # 尝试初始化PaddleOCR，但添加更多的错误处理
            try:
                import os
                # 设置环境变量以避免一些常见问题
                os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
                
                self.ocr_engine = PaddleOCR(
                    use_angle_cls=True,
                    lang="ch",
                    use_gpu=use_gpu,
                    ocr_version='PP-OCRv3',
                    show_log=False,  # 关闭详细日志输出
                    det_model_dir=None,  # 使用默认模型
                    rec_model_dir=None,  # 使用默认模型
                    cls_model_dir=None   # 使用默认模型
                )
                self.logger.info("PaddleOCR引擎初始化成功")
                
            except Exception as paddle_e:
                self.logger.warning(f"PaddleOCR初始化失败: {str(paddle_e)}")
                # 如果GPU初始化失败，尝试CPU模式
                if use_gpu:
                    self.logger.info("尝试使用CPU模式初始化PaddleOCR")
                    try:
                        self.ocr_engine = PaddleOCR(
                            use_angle_cls=True,
                            lang="ch",
                            use_gpu=False,  # 强制使用CPU
                            ocr_version='PP-OCRv3',
                            show_log=False
                        )
                        self.logger.info("PaddleOCR引擎(CPU模式)初始化成功")
                    except Exception as cpu_e:
                        self.logger.error(f"PaddleOCR CPU模式也失败: {str(cpu_e)}")
                        self.ocr_engine = None
                else:
                    self.ocr_engine = None
            """
            
        except Exception as e:
            self.logger.error(f"OCR引擎初始化失败，将使用备用方案: {str(e)}")
            Logger.log_error_with_context(e, "OCR引擎初始化")
            self.ocr_engine = None
    
    def recognize_text(self, image: np.ndarray) -> List[str]:
        """识别图像中的文本"""
        try:
            # 检查输入图像
            if image is None or image.size == 0:
                self.logger.warning("输入图像为空")
                return []
            
            # 检查图像尺寸
            if len(image.shape) < 2:
                self.logger.warning("图像尺寸不正确")
                return []
            
            height, width = image.shape[:2]
            if height < 10 or width < 10:
                self.logger.warning(f"图像尺寸过小: {width}x{height}")
                return []
            
            if self.ocr_engine is None:
                # 备用方案：使用Tesseract或其他OCR
                return self._fallback_ocr(image)
            
            # 使用PaddleOCR进行识别
            try:
                result = self.ocr_engine.ocr(image, cls=True)
            except Exception as ocr_e:
                self.logger.warning(f"PaddleOCR识别失败，尝试备用方案: {str(ocr_e)}")
                return self._fallback_ocr(image)
            
            # 提取识别结果中的文本
            texts = []
            if result and result[0]:
                for line in result[0]:
                    try:
                        if line and len(line) >= 2:
                            text = line[1][0]  # 提取文本内容
                            confidence = line[1][1]  # 置信度
                            if confidence > 0.5:  # 置信度阈值
                                texts.append(text.strip())
                    except (IndexError, TypeError) as parse_e:
                        self.logger.debug(f"解析OCR结果时出错: {str(parse_e)}")
                        continue
            
            self.logger.debug(f"识别到 {len(texts)} 个文本片段")
            return texts
            
        except Exception as e:
            self.logger.error(f"文本识别失败: {str(e)}")
            # 不抛出异常，返回空列表
            return []
    
    def _fallback_ocr(self, image: np.ndarray) -> List[str]:
        """备用OCR方案（当PaddleOCR不可用时）"""
        try:
            # 尝试使用Tesseract
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
                self.logger.warning("pytesseract未安装，使用简单文本提取")
                return self._simple_text_extraction(image)
            except Exception as tesseract_e:
                self.logger.warning(f"Tesseract OCR失败: {str(tesseract_e)}，使用简单文本提取")
                return self._simple_text_extraction(image)
                
        except Exception as e:
            self.logger.error(f"备用OCR失败: {str(e)}")
            return []
    
    def _simple_text_extraction(self, image: np.ndarray) -> List[str]:
        """简单的文本提取方法（不依赖外部OCR库）"""
        try:
            # 这是一个非常简单的方法，主要用于避免程序崩溃
            # 实际应用中应该使用真正的OCR
            
            # 检查图像中是否有足够的对比度来包含文本
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # 计算图像的标准差，如果太低可能没有文本
            std_dev = np.std(gray)
            if std_dev < 10:
                return []
            
            # 简单的二值化
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 查找轮廓，可能的文本区域
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 如果有足够的轮廓，假设可能有文本
            if len(contours) > 5:
                # 返回一些占位符文本，表示检测到可能的文本区域
                return ["检测到文本区域"]
            else:
                return []
                
        except Exception as e:
            self.logger.debug(f"简单文本提取失败: {str(e)}")
            return []
    
    def extract_date_info(self, text_results: List[str]) -> Dict:
        """从OCR结果中提取日期信息"""
        date_info = {}
        
        # 多种年月匹配模式
        year_month_patterns = [
            r'(\d{4})年(\d{1,2})月',  # 2025年09月
            r'(\d{4})年0?(\d{1,2})月',  # 2025年9月 或 2025年09月
            r'(\d{4})\s*年\s*(\d{1,2})\s*月',  # 带空格的情况
            r'(\d{4})-(\d{1,2})',  # 2025-09
            r'(\d{4})\.(\d{1,2})',  # 2025.09
            r'(\d{4})/(\d{1,2})',  # 2025/09
        ]
        
        # 匹配日期（如：1日、15日）
        day_pattern = r'(\d{1,2})日?'
        # 匹配星期（如：周一、星期二）
        weekday_pattern = r'周[一二三四五六日天]|星期[一二三四五六日天]'
        
        # 合并所有文本进行整体匹配
        combined_text = ' '.join(text_results)
        self.logger.debug(f"合并文本用于日期提取: {combined_text}")
        
        # 优先匹配年月信息
        for pattern in year_month_patterns:
            year_month_match = re.search(pattern, combined_text)
            if year_month_match:
                try:
                    year = int(year_month_match.group(1))
                    month = int(year_month_match.group(2))
                    if 2020 <= year <= 2030 and 1 <= month <= 12:  # 合理性检查
                        date_info['year'] = year
                        date_info['month'] = month
                        self.logger.info(f"提取到年月信息: {year}年{month}月")
                        break
                except (ValueError, IndexError):
                    continue
        
        # 逐个文本片段匹配其他信息
        for text in text_results:
            # 如果还没有年月信息，再次尝试匹配
            if 'year' not in date_info or 'month' not in date_info:
                for pattern in year_month_patterns:
                    year_month_match = re.search(pattern, text)
                    if year_month_match:
                        try:
                            year = int(year_month_match.group(1))
                            month = int(year_month_match.group(2))
                            if 2020 <= year <= 2030 and 1 <= month <= 12:
                                date_info['year'] = year
                                date_info['month'] = month
                                self.logger.info(f"从单个文本提取到年月信息: {year}年{month}月")
                                break
                        except (ValueError, IndexError):
                            continue
            
            # 尝试匹配日期
            day_match = re.search(day_pattern, text)
            if day_match:
                try:
                    day = int(day_match.group(1))
                    if 1 <= day <= 31:  # 合理性检查
                        date_info['day'] = day
                except (ValueError, IndexError):
                    continue
            
            # 尝试匹配星期
            weekday_match = re.search(weekday_pattern, text)
            if weekday_match:
                weekday = weekday_match.group()
                date_info['weekday'] = weekday
        
        self.logger.debug(f"提取的日期信息: {date_info}")
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
