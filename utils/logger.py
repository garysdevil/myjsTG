# logger.py
import logging
from datetime import datetime
import os

def setup_logger(name: str, log_file: str = 'gdefault.log', to_console: bool = True) -> logging.Logger:
    """设置日志记录器，可选择是否输出到控制台
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件名称，默认为 'gdefault.log'
        to_console: 是否同时输出到控制台，默认为 True
    
    Returns:
        配置好的日志记录器
    """
    # 创建日志目录如果不存在
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建完整的日志文件路径
    log_path = os.path.join(log_dir, log_file)
    
    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 如果已经有handler，就先清除
    if logger.handlers:
        logger.handlers.clear()
    
    # 创建文件handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    
    # 定义日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 设置文件handler格式
    file_handler.setFormatter(formatter)
    
    # 添加文件handler到logger
    logger.addHandler(file_handler)
    
    # 如果需要输出到控制台
    if to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str = 'logger_tg', 
              log_file: str = datetime.now().strftime('%Y%m%d.log'), 
              to_console: bool = True) -> logging.Logger:
    """获取全局唯一的logger实例
    
    Args:
        name: 日志记录器名称，默认为 'logger_tg'
        log_file: 日志文件名称，默认为当前日期格式 'YYYYMMDD.log' (如 '20250305.log')
        to_console: 是否同时输出到控制台，默认为 True
    
    Returns:
        配置好的日志记录器
    """
    return setup_logger(name, log_file, to_console)

# 示例使用
if __name__ == "__main__":
    # 默认同时输出到文件和控制台
    logger = get_logger('test_logger')
    logger.info("This will appear in both file and console")
    
    # 只输出到文件
    logger_no_console = get_logger('test_no_console', to_console=False)
    logger_no_console.info("This will only appear in the log file")