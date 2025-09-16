#!/usr/bin/env python3
"""
简单调试脚本 - 不使用OCR
"""
import sys
import logging
from pathlib import Path
import cv2
import numpy as np

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from attendance_assistant.core.config_manager import ConfigManager
from attendance_assistant.services.image_processor import ImageProcessor

def setup_logging():
    """设置简单的日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

def test_basic_processing(image_path: str):
    """测试基本图像处理（不包含OCR）"""
    logger = logging.getLogger(__name__)
    
    try:
        # 初始化配置
        config = ConfigManager()
        
        # 初始化处理器
        image_processor = ImageProcessor(config)
        
        logger.info(f"开始测试基本图像处理: {image_path}")
        
        # 1. 加载图像
        logger.info("步骤1: 加载图像")
        original_image = image_processor.load_image(image_path)
        logger.info(f"图像尺寸: {original_image.shape}")
        
        # 2. 预处理
        logger.info("步骤2: 图像预处理")
        processed_image = image_processor.preprocess_image(original_image)
        logger.info(f"预处理后图像尺寸: {processed_image.shape}")
        
        # 3. 检测表格单元格
        logger.info("步骤3: 检测表格单元格")
        cells = image_processor.detect_table_cells(processed_image)
        logger.info(f"检测到 {len(cells)} 个单元格")
        
        if len(cells) == 0:
            logger.warning("未检测到任何单元格")
            return False
        
        # 显示单元格信息
        logger.info("单元格信息:")
        for i, cell in enumerate(cells[:10]):  # 只显示前10个
            logger.info(f"单元格 {i+1}: 位置({cell.x},{cell.y}) 尺寸({cell.width}x{cell.height}) 行列({cell.row},{cell.col})")
        
        # 4. 测试提取单元格图像
        logger.info("步骤4: 测试提取单元格图像")
        test_count = min(3, len(cells))
        
        for i, cell in enumerate(cells[:test_count]):
            try:
                logger.info(f"提取单元格 {i+1}/{test_count}")
                
                # 检查单元格边界
                if (cell.x + cell.width > original_image.shape[1] or 
                    cell.y + cell.height > original_image.shape[0]):
                    logger.warning(f"单元格 {i+1} 边界超出图像范围")
                    continue
                
                # 提取单元格图像
                cell_image = image_processor.extract_cell_image(original_image, cell)
                if cell_image is None or cell_image.size == 0:
                    logger.warning(f"单元格 {i+1} 图像为空")
                    continue
                    
                logger.info(f"单元格 {i+1} 图像尺寸: {cell_image.shape}")
                
                # 测试圆点检测（不使用OCR）
                try:
                    dots = image_processor.detect_dots(cell_image)
                    logger.info(f"单元格 {i+1} 检测到 {len(dots)} 个圆点")
                except Exception as dot_e:
                    logger.warning(f"单元格 {i+1} 圆点检测失败: {str(dot_e)}")
                
            except Exception as cell_e:
                logger.error(f"处理单元格 {i+1} 时出错: {str(cell_e)}")
                continue
        
        logger.info("基本处理测试完成")
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python simple_debug.py <图片路径>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"图片文件不存在: {image_path}")
        sys.exit(1)
    
    setup_logging()
    
    success = test_basic_processing(image_path)
    
    if success:
        print("基本处理测试成功")
        sys.exit(0)
    else:
        print("基本处理测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main()