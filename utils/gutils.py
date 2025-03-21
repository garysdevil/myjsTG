import os
from typing import Dict
from utils import logger

# 初始化 logger，默认同时输出到文件和控制台
bit_logger = logger.get_logger('bit_log', to_console=True)

def list_files_in_directory(directory_path):
    # 列出指定目录中的所有文件和子目录
    files = os.listdir(directory_path)
    # 只保留文件（排除子目录）
    files = [f for f in files if os.path.isfile(os.path.join(directory_path, f))]
    return files

def list_file_paths_in_directory(directory_path):
    # 获取指定目录中所有文件的完整路径
    file_paths = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    return file_paths


def parse_proxy(proxy_str: str) -> Dict:
    """
    解析代理字符串，格式为 'host:port:username:password'
    参考: https://github.com/Anorov/PySocks#usage-1
    
    Args:
        proxy_str (str): 代理字符串
        
    Returns:
        Dict: 代理配置字典
        
    Raises:
        ValueError: 如果代理格式无效
    """
    try:
        parts = proxy_str.split(':')
        if len(parts) != 4:
            raise ValueError("Proxy string must have 4 parts: host:port:username:password")
        host, port, username, password = parts
        return {
            "proxy_type": "socks5",  # 默认 SOCKS5 协议
            "addr": host,
            "port": int(port),
            "rdns": True,  # 默认使用远程 DNS 解析
            "username": username,
            "password": password
        }
    except Exception as e:
        raise ValueError(f"Invalid proxy format: {proxy_str}, error: {str(e)}")

def write_file(file_name, data, mode='a'):
    """
    将数据写入文件，并确保立即写入磁盘。
    :param file_name: 文件名
    :param data: 要写入的数据（字符串或列表）
    :param mode: 文件打开模式，默认为追加模式 ('a')
    """
    try:
        # 使用 os.path.join 确保路径分隔符正确
        path = os.path.join(os.getcwd(), file_name)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, mode, newline="") as wf:
            # 处理单一字符串或列表
            if isinstance(data, str):
                wf.write(data + '\n')  # 写入字符串并加换行符
            else:
                wf.writelines([line + '\n' if not line.endswith('\n') else line for line in data])
            wf.flush()  # 立即刷新缓冲区
            os.fsync(wf.fileno())  # 同步到磁盘
            bit_logger.info(f"Successfully wrote to {path}")
    except Exception as e:
        bit_logger.error(f"Failed to write to {path}: {str(e)}")

def read_file(file_name):
    """
    读取txt文件并返回每行数据的列表。
    :param file_name: 文件名
    :return: 包含每行数据的列表
    """
    lines = []
    with open(file_name, 'r', encoding="UTF-8") as file_to_read:
        lines = file_to_read.readlines()
    return lines

def clear_file(filename):
    with open(filename, "w") as file:
        file.write("")

if __name__ == "__main__":
    write_file('local/aa.txt','11')
    # print(a)