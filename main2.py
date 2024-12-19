from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
import json
import random
import time
from log import logging, error_logger  # 引入日志模块

from gconfig import ginit
import gtele.gfuncs as gfuncs
import gtele.gjoingroup as gjoingroup
from gutils import gdata

# 主程序逻辑
async def main(data_file='local/data.txt', key_folder='local/keys', start_line=1, end_line=None):
    """
    主程序：
    1. 读取数据文件，获取账号和代理信息。
    2. 循环处理每个账号，进行登录操作。
    3. 随机延时，避免频繁请求导致封禁。
    """
    # 读取提取的数据
    extracted_data = json.loads(gdata.get_extracted_data(data_file))

    # 读取配置参数
    config = ginit.config()
    api_id = config['dev']['api_id']  # Telegram API ID
    api_hash = config['dev']['api_hash']  # Telegram API Hash
    password = config['account']['password']  # 两步验证密码（未设置可为空）
    old_password = config['account']['oldpassword']  # 两步验证密码（未设置可为空）

    # 遍历数据文件，从指定行号开始处理
    for idx, item in enumerate(extracted_data, start=1):
        if idx < start_line:
            continue  # 跳过起始行号之前的行
        
        if end_line and idx > end_line:
            logging.info(f"已达到终止行号 {end_line}，停止处理。")
            break
        
        phone = item["phone"]
        code_url = item["code_url"]
        proxy = item["proxy"]
        key_path = key_folder + f"/{phone}.session"

        logging.info(f"\n[{idx}] 正在处理账号: {phone}，使用代理: {proxy}")
    
        # 从文件读取已保存的 StringSession
        with open(key_path, "r") as file:
            session_str = file.read().strip()

        # 使用 StringSession 初始化 TelegramClient
        client = TelegramClient(StringSession(session_str), api_id, api_hash)

        # 设置代理（如果有）
        if proxy:
            client.session.proxies = {
                "http": proxy,
                "https": proxy
            }

        await client.connect()
        
        await change_password(client, phone, password, old_password)  # 更改2fa密码

        # 添加随机延时，避免频繁请求
        delay = random.uniform(2, 5)
        logging.info(f"操作完成，延时 {delay:.2f} 秒后继续...")
        time.sleep(delay)
        
async def change_password(client: TelegramClient, phone: str, new_password: str, old_password: str):
        result = await gfuncs.change_password(client, new_password, old_password) # 更改2fa密码
        logging.info(f"{phone} {result}")

# 命令行入口
if __name__ == "__main__":
    import argparse

    # 命令行参数解析
    parser = argparse.ArgumentParser(description="Telegram 自动登录程序")
    parser.add_argument('--data-file', type=str, default='local/data.txt', help="指定数据文件路径，默认为 'local/data.txt'")
    parser.add_argument('--key-folder', type=str, default='local/keys', help="指定 Session 文件保存路径，默认为 'local/keys'")
    parser.add_argument('--start-line', type=int, default=1, help="指定从哪一行开始处理")
    parser.add_argument('--end-line', type=int, help="指定在某一行结束处理（可选，不指定则处理到文件结束）")
    args = parser.parse_args()

    # 异步运行主程序
    asyncio.run(main(data_file=args.data_file, key_folder=args.key_folder, start_line=args.start_line, end_line=args.end_line))
