#!/usr/bin/env python3
"""
日志清理工具
用于清理旧的日志文件和压缩日志
"""
import argparse
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List


class LogCleanup:
    """日志清理工具"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        if not self.log_dir.exists():
            self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def get_log_files(self) -> List[Path]:
        """获取所有日志文件"""
        log_files = []
        for pattern in ['*.log', '*.log.*']:
            log_files.extend(self.log_dir.glob(pattern))
        return sorted(log_files)
    
    def compress_old_logs(self, days_old: int = 7):
        """压缩旧的日志文件"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        compressed_count = 0
        
        for log_file in self.get_log_files():
            # 跳过已压缩的文件
            if log_file.suffix == '.gz':
                continue
            
            # 检查文件修改时间
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_time < cutoff_date:
                compressed_file = log_file.with_suffix(log_file.suffix + '.gz')
                
                print(f"压缩文件: {log_file} -> {compressed_file}")
                
                with open(log_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # 删除原文件
                log_file.unlink()
                compressed_count += 1
        
        print(f"已压缩 {compressed_count} 个日志文件")
    
    def delete_old_logs(self, days_old: int = 30):
        """删除旧的日志文件"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        deleted_count = 0
        deleted_size = 0
        
        for log_file in self.get_log_files():
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_time < cutoff_date:
                file_size = log_file.stat().st_size
                print(f"删除文件: {log_file} ({self._format_size(file_size)})")
                
                log_file.unlink()
                deleted_count += 1
                deleted_size += file_size
        
        print(f"已删除 {deleted_count} 个日志文件，释放空间 {self._format_size(deleted_size)}")
    
    def get_log_statistics(self):
        """获取日志文件统计信息"""
        log_files = self.get_log_files()
        total_size = sum(f.stat().st_size for f in log_files)
        
        print(f"=== 日志文件统计 ===")
        print(f"日志目录: {self.log_dir}")
        print(f"文件总数: {len(log_files)}")
        print(f"总大小: {self._format_size(total_size)}")
        
        # 按类型分组
        by_type = {}
        for log_file in log_files:
            if log_file.suffix == '.gz':
                file_type = '压缩文件'
            elif log_file.suffix == '.log':
                file_type = '当前日志'
            else:
                file_type = '轮转日志'
            
            if file_type not in by_type:
                by_type[file_type] = {'count': 0, 'size': 0}
            
            by_type[file_type]['count'] += 1
            by_type[file_type]['size'] += log_file.stat().st_size
        
        print(f"\n按类型统计:")
        for file_type, stats in by_type.items():
            print(f"  {file_type}: {stats['count']} 个文件, {self._format_size(stats['size'])}")
        
        # 显示最大的文件
        if log_files:
            largest_files = sorted(log_files, key=lambda f: f.stat().st_size, reverse=True)[:5]
            print(f"\n最大的文件:")
            for i, log_file in enumerate(largest_files, 1):
                size = self._format_size(log_file.stat().st_size)
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                print(f"  {i}. {log_file.name} - {size} ({mtime})")
    
    def archive_logs(self, archive_name: str = None):
        """归档所有日志文件"""
        if archive_name is None:
            archive_name = f"logs_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        
        archive_path = self.log_dir.parent / archive_name
        
        import tarfile
        with tarfile.open(archive_path, 'w:gz') as tar:
            for log_file in self.get_log_files():
                tar.add(log_file, arcname=log_file.name)
        
        print(f"日志已归档到: {archive_path}")
        return archive_path
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='日志清理工具')
    parser.add_argument('--log-dir', default='logs', help='日志目录路径')
    parser.add_argument('--compress', type=int, metavar='DAYS', 
                       help='压缩N天前的日志文件')
    parser.add_argument('--delete', type=int, metavar='DAYS',
                       help='删除N天前的日志文件')
    parser.add_argument('--stats', '-s', action='store_true', help='显示统计信息')
    parser.add_argument('--archive', help='归档所有日志文件到指定文件名')
    
    args = parser.parse_args()
    
    # 创建清理工具
    cleanup = LogCleanup(args.log_dir)
    
    if args.stats:
        cleanup.get_log_statistics()
    
    if args.compress:
        cleanup.compress_old_logs(args.compress)
    
    if args.delete:
        cleanup.delete_old_logs(args.delete)
    
    if args.archive:
        cleanup.archive_logs(args.archive)
    
    # 如果没有指定任何操作，显示统计信息
    if not any([args.stats, args.compress, args.delete, args.archive]):
        cleanup.get_log_statistics()


if __name__ == '__main__':
    main()