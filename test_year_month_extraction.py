#!/usr/bin/env python3
"""
测试年月提取功能
"""
import re
import logging

# 设置日志
logging.basicConfig(level=logging.DEBUG)

def extract_date_info_test(text_results):
    """测试版本的日期信息提取"""
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
    
    # 合并所有文本进行整体匹配
    combined_text = ' '.join(text_results)
    print(f"合并文本用于日期提取: {combined_text}")
    
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
                    print(f"提取到年月信息: {year}年{month}月")
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
                            print(f"从单个文本提取到年月信息: {year}年{month}月")
                            break
                    except (ValueError, IndexError):
                        continue
    
    print(f"提取的日期信息: {date_info}")
    return date_info

def test_year_month_extraction():
    """测试年月提取功能"""
    # 测试不同格式的年月文本
    test_texts = [
        ["2025年09月"],
        ["2025年9月"],
        ["2025 年 09 月"],
        ["2025-09"],
        ["2025.09"],
        ["2025/09"],
        ["考勤表", "2025年09月"],
        ["打卡记录", "2025年9月份"],
        ["出勤统计 2025年09月"],
        ["2025年09月考勤表"],
        ["月份：2025年09月"],
        ["时间：2025年9月"],
    ]
    
    print("测试年月提取功能:")
    print("=" * 50)
    
    for i, texts in enumerate(test_texts, 1):
        print(f"\n测试 {i}: {texts}")
        date_info = extract_date_info_test(texts)
        print(f"提取结果: {date_info}")
        
        if date_info.get('year') and date_info.get('month'):
            year_month = f"{date_info['year']:04d}-{date_info['month']:02d}"
            print(f"格式化结果: {year_month}")
        else:
            print("未提取到年月信息")

if __name__ == "__main__":
    test_year_month_extraction()