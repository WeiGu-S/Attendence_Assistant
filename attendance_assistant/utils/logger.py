"""
日志管理工具
提供统一的日志记录接口
"""
import logging
from typing import Optional


class Logger:
    """日志管理器"""
    
    @staticmethod
    def get_logger(name: Optional[str] = None) -> logging.Logger:
        """
        获取日志记录器
        
        Args:
            name: 日志记录器名称，默认使用调用模块名
            
        Returns:
            logging.Logger: 日志记录器实例
        """
        if name is None:
            # 获取调用者的模块名
            import inspect
            frame = inspect.currentframe().f_back
            name = frame.f_globals.get('__name__', 'unknown')
        
        return logging.getLogger(name)
    
    @staticmethod
    def log_function_call(func_name: str, args: tuple = (), kwargs: dict = None):
        """
        记录函数调用
        
        Args:
            func_name: 函数名
            args: 位置参数
            kwargs: 关键字参数
        """
        logger = Logger.get_logger()
        kwargs = kwargs or {}
        
        # 构建参数字符串
        arg_strs = []
        if args:
            arg_strs.extend([str(arg) for arg in args])
        if kwargs:
            arg_strs.extend([f"{k}={v}" for k, v in kwargs.items()])
        
        arg_str = ", ".join(arg_strs)
        logger.debug(f"调用函数: {func_name}({arg_str})")
    
    @staticmethod
    def log_performance(operation: str, duration: float, details: str = ""):
        """
        记录性能信息
        
        Args:
            operation: 操作名称
            duration: 耗时（秒）
            details: 详细信息
        """
        logger = Logger.get_logger()
        detail_str = f" - {details}" if details else ""
        logger.info(f"性能统计: {operation} 耗时 {duration:.3f}秒{detail_str}")
    
    @staticmethod
    def log_error_with_context(error: Exception, context: str = ""):
        """
        记录带上下文的错误信息
        
        Args:
            error: 异常对象
            context: 上下文信息
        """
        logger = Logger.get_logger()
        context_str = f"[{context}] " if context else ""
        logger.error(f"{context_str}发生错误: {type(error).__name__}: {str(error)}", exc_info=True)


def performance_monitor(operation_name: str = ""):
    """
    性能监控装饰器
    
    Args:
        operation_name: 操作名称，默认使用函数名
    """
    def decorator(func):
        import functools
        import time
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            name = operation_name or func.__name__
            start_time = time.time()
            
            try:
                Logger.log_function_call(func.__name__, args, kwargs)
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                Logger.log_performance(name, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                Logger.log_performance(f"{name}(失败)", duration)
                Logger.log_error_with_context(e, name)
                raise
        
        return wrapper
    return decorator


# 便捷的日志记录函数
def debug(message: str, logger_name: str = None):
    """记录调试信息"""
    Logger.get_logger(logger_name).debug(message)


def info(message: str, logger_name: str = None):
    """记录信息"""
    Logger.get_logger(logger_name).info(message)


def warning(message: str, logger_name: str = None):
    """记录警告"""
    Logger.get_logger(logger_name).warning(message)


def error(message: str, logger_name: str = None):
    """记录错误"""
    Logger.get_logger(logger_name).error(message)


def critical(message: str, logger_name: str = None):
    """记录严重错误"""
    Logger.get_logger(logger_name).critical(message)