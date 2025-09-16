#!/usr/bin/env python3
"""
调试图像处理脚本
用于测试图像处理流程，帮助定位问题
"""
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from attendance_assistant.core.config_manager import ConfigManager
from attendance_assistant.services.image_processor import ImageProcessor
from attendance_assistant.services.ocr_service import OCRService

def setup_logging():
    """设置简单的日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

def test_image_processing(image_path: str):
    """测试图像处理流程"""
    logger = logging.getLogger(__name__)
    
    try:
        # 初始化配置
        config = ConfigManager()
        
        # 初始化处理器
        image_processor = ImageProcessor(config)
        
        logger.info(f"开始测试图像处理: {image_path}")
        
        # 1. 加载图像
        logger.info("步骤1: 加载图像")
        original_image = image_processor.load_image(image_path)
        logger.info(f"图像尺寸: {original_image.shape}")
        
        # 2. 预处理
        logger.info("步骤2: 图像预处理")
        processed_image = image_processor.preprocess_image(original_image)
        logger.info("预处理完成")
        
        # 3. 检测表格单元格
        logger.info("步骤3: 检测表格单元格")
        cells = image_processor.detect_table_cells(processed_image)
        logger.info(f"检测到 {len(cells)} 个单元格")
        
        if len(cells) == 0:
            logger.warning("未检测到任何单元格")
            return False
        
        # 显示前几个单元格的信息
        logger.info("前10个单元格信息:")
        for i, cell in enumerate(cells[:10]):
            logger.info(f"单元格 {i+1}: 位置({cell.x},{cell.y}) 尺寸({cell.width}x{cell.height}) 行列({cell.row},{cell.col})")
        
        # 4. 初始化OCR服务（分开初始化以便定位问题）
        logger.info("步骤4: 初始化OCR服务")
        try:
            # 禁用GPU以避免内存问题
            config.set('OCR', 'use_gpu', 'False')
            ocr_service = OCRService(config)
            logger.info("OCR服务初始化成功")
        except Exception as ocr_init_e:
            logger.error(f"OCR服务初始化失败: {str(ocr_init_e)}")
            return False
        
        # 5. 测试处理前几个单元格
        logger.info("步骤5: 测试处理单元格")
        test_count = min(3, len(cells))  # 只测试前3个单元格
        
        for i, cell in enumerate(cells[:test_count]):
            try:
                logger.info(f"处理单元格 {i+1}/{test_count}: ({cell.x},{cell.y},{cell.width},{cell.height})")
                
                # 检查单元格尺寸
                if cell.width < 20 or cell.height < 20:
                    logger.info(f"跳过过小的单元格 {i+1}")
                    continue
                
                # 提取单元格图像
                cell_image = image_processor.extract_cell_image(original_image, cell)
                if cell_image is None or cell_image.size == 0:
                    logger.info(f"单元格 {i+1} 图像为空，跳过")
                    continue
                    
                logger.info(f"单元格图像尺寸: {cell_image.shape}")
                
                # OCR识别（添加超时保护）
                try:
                    logger.info(f"开始OCR识别单元格 {i+1}")
                    texts = ocr_service.recognize_text(cell_image)
                    logger.info(f"识别到文本: {texts}")
                except Exception as ocr_e:
                    logger.warning(f"单元格 {i+1} OCR识别失败: {str(ocr_e)}")
                    texts = []
                
                # 圆点检测
                try:
                    logger.info(f"开始圆点检测单元格 {i+1}")
                    dots = image_processor.detect_dots(cell_image)
                    logger.info(f"检测到 {len(dots)} 个圆点")
                except Exception as dot_e:
                    logger.warning(f"单元格 {i+1} 圆点检测失败: {str(dot_e)}")
                    dots = []
                
            except Exception as cell_e:
                logger.error(f"处理单元格 {i+1} 时出错: {str(cell_e)}")
                continue
        
        logger.info("测试完成")
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python debug_image_processing.py <图片路径>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"图片文件不存在: {image_path}")
        sys.exit(1)
    
    setup_logging()
    
    success = test_image_processing(image_path)
    
    if success:
        print("测试成功完成")
        sys.exit(0)
    else:
        print("测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main()