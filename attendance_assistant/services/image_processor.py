"""
图像处理模块
负责图像加载、预处理、表格检测和圆点识别
"""
import logging
import os
import cv2
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CellInfo:
    """表格单元格信息"""
    x: int  # 单元格左上角x坐标
    y: int  # 单元格左上角y坐标
    width: int  # 单元格宽度
    height: int  # 单元格高度
    row: int  # 行索引
    col: int  # 列索引
    content: Optional[str] = None  # 单元格内容


@dataclass
class DotInfo:
    """圆点检测信息"""
    x: int  # 圆点中心x坐标
    y: int  # 圆点中心y坐标
    color: str  # 圆点颜色: "green", "gray"
    radius: int  # 圆点半径


class ImageProcessor:
    """图像处理器类"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def load_image(self, image_path: str) -> np.ndarray:
        """加载图片并返回numpy数组"""
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图片文件不存在: {image_path}")
            
            # 检查文件大小
            file_size = os.path.getsize(image_path)
            if file_size == 0:
                raise ValueError(f"图片文件为空: {image_path}")
            
            # 使用cv2.IMREAD_COLOR确保加载彩色图像
            image = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError(f"无法加载图片，可能是不支持的格式: {image_path}")
            
            self.logger.info(f"成功加载图片: {image_path}, 尺寸: {image.shape}, 大小: {file_size} bytes")
            return image
        except Exception as e:
            self.logger.error(f"图片加载失败: {str(e)}")
            raise
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        图像预处理流程:
        1. 灰度化
        2. 高斯模糊去噪
        3. 二值化(OTSU)
        4. 形态学操作(闭运算)
        """
        try:
            # 1. 灰度化
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 2. 高斯模糊去噪
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # 3. 二值化(OTSU)
            _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 4. 形态学操作(闭运算)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            self.logger.info("图像预处理完成")
            return closed
            
        except Exception as e:
            self.logger.error(f"图像预处理失败: {str(e)}")
            raise
    
    def detect_table_cells(self, processed_image: np.ndarray) -> List[CellInfo]:
        """
        检测表格单元格位置
        返回: 单元格信息列表
        """
        try:
            # 使用轮廓检测找到表格单元格
            contours, _ = cv2.findContours(
                processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            cells = []
            for contour in contours:
                # 过滤掉太小的轮廓
                area = cv2.contourArea(contour)
                if area < 100:  # 最小面积阈值
                    continue
                
                # 获取边界矩形
                x, y, w, h = cv2.boundingRect(contour)
                
                # 创建单元格信息
                cell = CellInfo(
                    x=x, y=y, width=w, height=h,
                    row=-1, col=-1, content=None
                )
                cells.append(cell)
            
            # 根据位置对单元格进行排序和行列分配
            self._assign_cell_positions(cells)
            
            self.logger.info(f"检测到 {len(cells)} 个表格单元格")
            return cells
            
        except Exception as e:
            self.logger.error(f"表格单元格检测失败: {str(e)}")
            raise
    
    def _assign_cell_positions(self, cells: List[CellInfo]):
        """为单元格分配行列位置"""
        if not cells:
            return
            
        # 按y坐标排序分组行
        cells.sort(key=lambda cell: cell.y)
        
        # 分组行
        rows = []
        current_row = [cells[0]]
        row_y_threshold = cells[0].height * 0.5  # 行高的一半作为阈值
        
        for i in range(1, len(cells)):
            if abs(cells[i].y - current_row[-1].y) < row_y_threshold:
                current_row.append(cells[i])
            else:
                # 对当前行按x坐标排序
                current_row.sort(key=lambda cell: cell.x)
                rows.append(current_row)
                current_row = [cells[i]]
        
        # 添加最后一行
        if current_row:
            current_row.sort(key=lambda cell: cell.x)
            rows.append(current_row)
        
        # 分配行列索引
        for row_idx, row in enumerate(rows):
            for col_idx, cell in enumerate(row):
                cell.row = row_idx
                cell.col = col_idx
                
        self.logger.info(f"分配了 {len(rows)} 行，每行单元格数: {[len(row) for row in rows]}")
    
    def extract_cell_image(self, original_image: np.ndarray, cell_info: CellInfo) -> np.ndarray:
        """提取单个单元格图像"""
        try:
            # 提取单元格区域
            cell_img = original_image[
                cell_info.y:cell_info.y + cell_info.height,
                cell_info.x:cell_info.x + cell_info.width
            ]
            return cell_img
        except Exception as e:
            self.logger.error(f"提取单元格图像失败: {str(e)}")
            raise
    
    def detect_dots(self, cell_image: np.ndarray) -> List[DotInfo]:
        """
        检测单元格内的圆点
        返回: 圆点信息列表
        """
        try:
            dots = []
            
            # 转换到HSV颜色空间进行颜色检测
            hsv = cv2.cvtColor(cell_image, cv2.COLOR_BGR2HSV)
            
            # 定义绿色圆点的HSV范围
            green_lower = np.array([35, 50, 50])
            green_upper = np.array([85, 255, 255])
            
            # 定义灰色圆点的HSV范围
            gray_lower = np.array([0, 0, 50])
            gray_upper = np.array([180, 50, 200])
            
            # 检测绿色圆点
            green_mask = cv2.inRange(hsv, green_lower, green_upper)
            green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in green_contours:
                # 过滤掉太小的轮廓
                area = cv2.contourArea(contour)
                if area < 10:  # 最小面积阈值
                    continue
                
                # 获取最小外接圆
                (x, y), radius = cv2.minEnclosingCircle(contour)
                center = (int(x), int(y))
                radius = int(radius)
                
                # 计算圆度
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if circularity > 0.7:  # 圆度阈值
                        dot = DotInfo(
                            x=center[0], y=center[1], 
                            color="green", radius=radius
                        )
                        dots.append(dot)
            
            # 检测灰色圆点
            gray_mask = cv2.inRange(hsv, gray_lower, gray_upper)
            gray_contours, _ = cv2.findContours(gray_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in gray_contours:
                # 过滤掉太小的轮廓
                area = cv2.contourArea(contour)
                if area < 10:  # 最小面积阈值
                    continue
                
                # 获取最小外接圆
                (x, y), radius = cv2.minEnclosingCircle(contour)
                center = (int(x), int(y))
                radius = int(radius)
                
                # 计算圆度
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if circularity > 0.7:  # 圆度阈值
                        dot = DotInfo(
                            x=center[0], y=center[1], 
                            color="gray", radius=radius
                        )
                        dots.append(dot)
            
            self.logger.debug(f"检测到 {len(dots)} 个圆点")
            return dots
            
        except Exception as e:
            self.logger.error(f"圆点检测失败: {str(e)}")
            raise
