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

from utils.gdata import get_extracted_data
from config import ginit

# 主函数
async def main(data_file='local/data.txt', key_folder='local/keys', start_line=1, end_line=None):

    # 获取提取的数据
    extracted_data = json.loads(get_extracted_data(data_file))

    # 配置参数
    config = ginit.config()
    api_id = config['dev']['api_id']  # 替换为您的 API ID
    api_hash = config['dev']['api_hash']  # 替换为您的 API Hash
    password = config['account']['password']  # 两步验证密码（未设置可为空）

    # 循环处理每一条数据，从指定行开始
    for idx, item in enumerate(extracted_data, start=1):
        if idx < start_line:
            continue  # 跳过起始行号之前的行
        
        if end_line and idx > end_line:
            print(f"已达到终止行号 {end_line}，停止处理。")
            break  # 如果当前行号超过终止行号，则结束循环
        
        phone = item["phone"]
        code_url = item["code_url"]
        proxy = item["proxy"]

        print(f"\n[{idx}] 正在处理账号: {phone}，使用代理: {proxy}")
        
        # 调用登录逻辑
        await login(api_id, api_hash, phone, password, key_folder, code_url, proxy)
        
        # 添加随机延时 3～6 秒
        delay = random.uniform(3, 6)
        print(f"操作完成，延时 {delay:.2f} 秒后继续...")
        time.sleep(delay)

# 设置代理（如果传递代理参数）
def get_code_from_url(url, proxy=None):
    """
    通过指定的 URL 获取验证码，支持传递代理
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

        # 使用代理设置
        proxies = {
            "http": proxy,
            "https": proxy
        } if proxy else None

        response = requests.get(url, proxies=proxies, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("code")
        else:
            print(f"请求验证码失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"获取验证码时出错: {e}")
    return None


# 创建保存 Session 的文件夹
def ensure_key_folder_exists(key_folder):
    """
    确保 Session 文件夹存在
    """
    if not os.path.exists(key_folder):
        os.makedirs(key_folder)

# 获取保存 Session 文件的路径
def get_session_file_path(key_folder, phone):
    """
    获取根据手机号命名的 Session 文件路径
    """
    return os.path.join(key_folder, f"{phone}.session")

# 登录 Telegram 客户端
async def login_to_telegram(client, phone, code_url, password, proxy=None):
    """
    使用验证码登录 Telegram，并处理两步验证，支持代理
    """
    if not await client.is_user_authorized():
        print(f"发送验证码请求到 {phone} ...")
        await client.send_code_request(phone)

        # 获取验证码并尝试登录
        print(f"尝试从 {code_url} 获取验证码...")
        code = get_code_from_url(code_url, proxy)
        if code:
            # 使用验证码进行登录
            print(f"使用验证码 {code} 登录...")
            try:
                await client.sign_in(phone=phone, code=code)  # 尝试使用验证码登录
            except SessionPasswordNeededError:
                if password:
                    print("两步验证启用，尝试使用密码登录...")
                    await client.sign_in(password=password)  # 提供两步验证密码
                else:
                    print("两步验证密码未提供，登录失败。")
                    return

        else:
            print("未获取到验证码，登录中止。")
            return False
    else:
        print("用户已经授权，无需重新登录。")
    return True

# 保存 Session 到文件
def save_session_to_file(client, session_file):
    """
    将客户端的 Session 保存到文件
    """
    with open(session_file, 'w') as f:
        f.write(client.session.save())
    print(f"Session 已保存到文件: {session_file}")
    print("保留好这个 session 字符串, 下次登录可以直接用这个字符串登录, 无需输入手机号和密码: \n", client.session.save())

# 登录逻辑
async def login(api_id, api_hash, phone, password, key_folder, code_url, proxy=None):
    """
    执行登录逻辑，管理 Telegram 客户端的连接、验证、Session 保存等操作
    """
    # 确保 Session 文件夹存在
    ensure_key_folder_exists(key_folder)

    # 获取 Session 文件路径
    session_file = get_session_file_path(key_folder, phone)

    # 创建 Telegram 客户端，传入代理
    client = TelegramClient(StringSession(), api_id, api_hash, connection=ConnectionTcpFull)

    # 如果代理存在，设置代理
    if proxy:
        client.session.proxies = {
            "http": proxy,
            "https": proxy
        }

    await client.connect()

    # 登录并保存 Session
    if await login_to_telegram(client, phone, code_url, password, proxy):
        save_session_to_file(client, session_file)

    await client.disconnect()


# 执行主程序
if __name__ == "__main__":
    # 从命令行传递 `start_line`, `end_line`, `data_file` 参数
    import argparse
    parser = argparse.ArgumentParser(description="Telegram 自动登录程序")
    parser.add_argument('--data-file', type=str, default='local/data.txt', help="指定数据文件路径，默认为 'local/local.data'")
    parser.add_argument('--key-folder', type=str, default='local/keys', help="指定sessionstr输出文件夹路径，默认为 'local/keys'")
    parser.add_argument('--start-line', type=int, default=1, help="指定从哪一行开始处理")
    parser.add_argument('--end-line', type=int, help="指定在某一行结束处理（可选，不指定则默认处理到最后一行）")
    args = parser.parse_args()

    # 执行主程序，传入从命令行获取的 start_line 和 end_line 参数
    asyncio.run(main(data_file=args.data_file, key_folder=args.key_folder, start_line=args.start_line, end_line=args.end_line))
