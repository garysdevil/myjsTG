import os
from urllib.parse import quote
import requests
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
from telethon.network.connection import ConnectionTcpFull
import asyncio
import json
import time
import random

from gutils import gdata
from gconfig import ginit
from log import logging, error_logger  # 引入日志模块


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

        logging.info(f"\n[{idx}] 正在处理账号: {phone}，使用代理: {proxy}")
        
        # 调用登录逻辑
        await login(api_id, api_hash, phone, password, key_folder, code_url, proxy)
        
        # 添加随机延时，避免频繁请求
        delay = random.uniform(2, 5)
        logging.info(f"操作完成，延时 {delay:.2f} 秒后继续...")
        time.sleep(delay)


def get_code_from_url(url, proxy=None):
    """
    从指定 URL 获取验证码。
    支持通过代理获取验证码，并提供手动输入验证码的备选方案。
    """
    try:
        if proxy:
            # 解析代理 URL 格式：socks5://username:password@host:port
            scheme, rest = proxy.split("://")
            userinfo, hostport = rest.split("@")
            username, password = userinfo.split(":")
            host, port = hostport.split(":")
            
            # 对用户名和密码进行 URL 编码
            username = quote(username)
            password = quote(password)
            
            # 构造新的代理 URL
            proxy = f"{scheme}://{username}:{password}@{host}:{port}"

        # 设置代理配置
        proxies = {
            "http": proxy,
            "https": proxy
        } if proxy else None

        # 请求验证码
        response = requests.get(url, proxies=proxies, timeout=10)
        if response.status_code == 200:
            data = response.json()
            code = data.get("code")
            if code:
                return code
            else:
                logging.warning("未在响应中找到验证码。")
        else:
            logging.warning(f"请求验证码失败，状态码: {response.status_code}")
    except Exception as e:
        error_logger.error(f"获取验证码时出错: {e}")

    # 提供手动输入验证码的选项
    while True:
        manual_code = input("无法自动获取验证码，请手动输入验证码：")
        if manual_code.strip():
            return manual_code
        print("验证码不能为空，请重新输入。")
    
    # return None

def ensure_key_folder_exists(key_folder):
    """
    确保保存 Session 的文件夹存在。
    """
    if not os.path.exists(key_folder):
        os.makedirs(key_folder)


def get_session_file_path(key_folder, phone):
    """
    获取 Session 文件路径。
    文件以手机号命名，存放在指定文件夹中。
    """
    return os.path.join(key_folder, f"{phone}.session")


async def login_to_telegram(client: TelegramClient, phone, code_url, password, proxy=None):
    """
    登录 Telegram 客户端：
    - 使用验证码登录。
    - 支持两步验证。
    - 支持自动获取验证码和手动输入验证码。
    """
    if not await client.is_user_authorized():
        logging.info(f"发送验证码请求到 {phone} ...")
        await client.send_code_request(phone)

        # 获取验证码并尝试登录
        logging.info(f"延迟1秒钟后，尝试从 {code_url} 获取验证码...")
        time.sleep(1)
        code = get_code_from_url(code_url, proxy)
        print(code)
        if code:
            try:
                logging.info(f"使用验证码 {code} 登录...")
                await client.sign_in(phone=phone, code=code)
            except SessionPasswordNeededError:
                if password:
                    logging.info("两步验证启用，尝试使用密码登录...")
                    await client.sign_in(password=password)
                else:
                    error_logger.error("两步验证密码未提供，登录失败。")
                    return False
        else:
            error_logger.error("未获取到验证码，登录中止。")
            return False
    else:
        logging.info("用户已授权，无需重新登录。")
    return True


def save_session_to_file(client: TelegramClient, session_file):
    """
    保存 Telegram 会话到文件。
    会话文件可用于下次直接登录，无需输入验证码或密码。
    """
    with open(session_file, 'w') as f:
        f.write(client.session.save())
    logging.info(f"Session 已保存到文件: {session_file}")
    logging.info(f"保存的 Session 字符串为: \n{client.session.save()}")


async def login(api_id, api_hash, phone, password, key_folder, code_url, proxy=None):
    """
    登录 Telegram：
    1. 确保保存 Session 的文件夹存在。
    2. 连接 Telegram 客户端，使用代理（如有）。
    3. 登录并保存会话。
    """
    ensure_key_folder_exists(key_folder)
    session_file = get_session_file_path(key_folder, phone)

    # 创建 Telegram 客户端
    client = TelegramClient(StringSession(), api_id, api_hash, connection=ConnectionTcpFull)

    # 设置代理（如果有）
    if proxy:
        client.session.proxies = {
            "http": proxy,
            "https": proxy
        }

    await client.connect()

    # 登录并保存会话
    if await login_to_telegram(client, phone, code_url, password, proxy):
        save_session_to_file(client, session_file)

    await client.disconnect()


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
