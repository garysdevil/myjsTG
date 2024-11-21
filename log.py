import logging
import os

# 创建日志目录
os.makedirs("logs", exist_ok=True)

# 配置普通日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/print.log", encoding="utf-8"),  # 普通日志文件
        logging.StreamHandler()  # 输出到控制台
    ]
)

# 配置错误日志
error_logger = logging.getLogger("error_logger")
error_file_handler = logging.FileHandler("logs/error.log", encoding="utf-8")
error_console_handler = logging.StreamHandler()

error_file_handler.setLevel(logging.ERROR)
error_console_handler.setLevel(logging.ERROR)

# 设置日志格式
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
error_file_handler.setFormatter(formatter)
error_console_handler.setFormatter(formatter)

# 添加处理器到错误日志
error_logger.addHandler(error_file_handler)
error_logger.addHandler(error_console_handler)
