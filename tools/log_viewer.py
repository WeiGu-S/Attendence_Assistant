#!/usr/bin/env python3
"""
日志查看工具
用于查看和分析应用日志
"""
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


class LogEntry:
    """日志条目"""
    
    def __init__(self, timestamp: datetime, level: str, logger: str, message: str, raw_line: str):
        self.timestamp = timestamp
        self.level = level
        self.logger = logger
        self.message = message
        self.raw_line = raw_line
    
    def __str__(self):
        return f"[{self.timestamp}] {self.level} - {self.logger}: {self.message}"


class LogViewer:
    """日志查看器"""
    
    def __init__(self, log_file: str = "logs/app.log"):
        self.log_file = Path(log_file)
        self.entries: List[LogEntry] = []
        self._load_logs()
    
    def _load_logs(self):
        """加载日志文件"""
        if not self.log_file.exists():
            print(f"日志文件不存在: {self.log_file}")
            return
        
        log_pattern = re.compile(
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - ([^-]+) - (\w+) - (.+)'
        )
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                match = log_pattern.match(line)
                if match:
                    timestamp_str, logger, level, message = match.groups()
                    try:
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                        entry = LogEntry(timestamp, level, logger.strip(), message, line)
                        self.entries.append(entry)
                    except ValueError:
                        # 如果时间戳解析失败，跳过这行
                        continue
    
    def filter_by_level(self, level: str) -> List[LogEntry]:
        """按日志级别过滤"""
        return [entry for entry in self.entries if entry.level == level.upper()]
    
    def filter_by_logger(self, logger_name: str) -> List[LogEntry]:
        """按日志记录器名称过滤"""
        return [entry for entry in self.entries if logger_name in entry.logger]
    
    def filter_by_time_range(self, start_time: datetime, end_time: datetime) -> List[LogEntry]:
        """按时间范围过滤"""
        return [entry for entry in self.entries 
                if start_time <= entry.timestamp <= end_time]
    
    def filter_by_message(self, pattern: str) -> List[LogEntry]:
        """按消息内容过滤（支持正则表达式）"""
        regex = re.compile(pattern, re.IGNORECASE)
        return [entry for entry in self.entries if regex.search(entry.message)]
    
    def get_statistics(self) -> Dict[str, int]:
        """获取日志统计信息"""
        stats = {
            'total': len(self.entries),
            'by_level': {},
            'by_logger': {}
        }
        
        for entry in self.entries:
            # 按级别统计
            stats['by_level'][entry.level] = stats['by_level'].get(entry.level, 0) + 1
            
            # 按记录器统计
            logger_name = entry.logger.split('.')[-1]  # 取最后一部分
            stats['by_logger'][logger_name] = stats['by_logger'].get(logger_name, 0) + 1
        
        return stats
    
    def get_recent_errors(self, hours: int = 24) -> List[LogEntry]:
        """获取最近的错误日志"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_entries = self.filter_by_time_range(cutoff_time, datetime.now())
        return [entry for entry in recent_entries if entry.level in ['ERROR', 'CRITICAL']]
    
    def print_entries(self, entries: List[LogEntry], limit: Optional[int] = None):
        """打印日志条目"""
        if limit:
            entries = entries[-limit:]  # 显示最新的N条
        
        for entry in entries:
            print(entry)
    
    def print_statistics(self):
        """打印统计信息"""
        stats = self.get_statistics()
        
        print(f"=== 日志统计信息 ===")
        print(f"总条目数: {stats['total']}")
        
        print(f"\n按级别统计:")
        for level, count in sorted(stats['by_level'].items()):
            print(f"  {level}: {count}")
        
        print(f"\n按模块统计:")
        for logger, count in sorted(stats['by_logger'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {logger}: {count}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='日志查看工具')
    parser.add_argument('--file', '-f', default='logs/app.log', help='日志文件路径')
    parser.add_argument('--level', '-l', help='按级别过滤 (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--logger', help='按记录器名称过滤')
    parser.add_argument('--message', '-m', help='按消息内容过滤（正则表达式）')
    parser.add_argument('--recent-errors', type=int, metavar='HOURS', 
                       help='显示最近N小时的错误日志')
    parser.add_argument('--stats', '-s', action='store_true', help='显示统计信息')
    parser.add_argument('--limit', type=int, help='限制显示条目数')
    parser.add_argument('--tail', '-t', type=int, help='显示最后N条日志')
    
    args = parser.parse_args()
    
    # 创建日志查看器
    viewer = LogViewer(args.file)
    
    if not viewer.entries:
        print("没有找到日志条目")
        return
    
    # 处理不同的命令
    if args.stats:
        viewer.print_statistics()
        return
    
    if args.recent_errors:
        entries = viewer.get_recent_errors(args.recent_errors)
        print(f"=== 最近 {args.recent_errors} 小时的错误日志 ===")
        viewer.print_entries(entries)
        return
    
    # 应用过滤器
    entries = viewer.entries
    
    if args.level:
        entries = [e for e in entries if e.level == args.level.upper()]
    
    if args.logger:
        entries = [e for e in entries if args.logger in e.logger]
    
    if args.message:
        regex = re.compile(args.message, re.IGNORECASE)
        entries = [e for e in entries if regex.search(e.message)]
    
    # 显示结果
    limit = args.tail or args.limit
    viewer.print_entries(entries, limit)


if __name__ == '__main__':
    main()