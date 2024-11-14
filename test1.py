#  pip install telethon
# 不行，TG账号一使用就被ban

from telethon import TelegramClient
from telethon.tl.types import User, Chat, Channel
from telethon.tl.functions.account import GetAuthorizationsRequest
import datetime
from getpass import getpass
import configparser
import tools
import asyncio

def init():
    config = configparser.ConfigParser()
    config.read('local.config.ini')

    proxy = {
        'proxy_type': config['proxy']['proxy_type'],  # 'http' or 'socks5'
        'addr': config['proxy']['addr'],  # 代理地址
        'port': int(config['proxy']['port']),             # 代理端口
        'username': config['proxy']['username'], # 代理用户名 (可选)
        'password': config['proxy']['password'], # 代理密码 (可选)
    }
    telegram = {
        'password': config['telegram']['password'],
        'session_path': config['telegram']['session_path'],
        'session_new_path': config['telegram']['session_new_path'],
        'api_id' : int(config['telegram']['api_id']),
        'api_hash' : config['telegram']['api_hash'],
    }
    return {'proxy': proxy, 'telegram': telegram}


async def main():
    config = init()
    password = config['telegram']['password']
    
    # 调用函数并打印文件列表
    directory_path = './local.session'  # 替换为你的文件夹路径
    filename_list = tools.list_files_in_directory(directory_path)

    filename = filename_list[0]
    sessionPath = r"./local.session/" + filename
    newSessionPath  = r"./local.new.session/" + filename

    print(filename)
    print(config['proxy'])

    # 创建 Telegram 客户端，使用现有的 session 文件
    client = TelegramClient(
        sessionPath,
        config['telegram']['api_id'],
        config['telegram']['api_hash'],
        # device_model='iPhone',  # 模拟 iPhone 设备
        # system_version='16.0',  # 模拟 iOS 版本
        # app_version='5.0.0',    # 设置应用版本
        proxy=config['proxy']            # 启用代理
    )
    # await client.loop.run_until_complete(test(client))
    await client.connect()
    await print_authorizations(client)
    # 断开连接
    await client.disconnect()

async def print_authorizations(client: TelegramClient):
    # 获取所有登录设备的授权状态
    authorizations = await client(GetAuthorizationsRequest())

    print("当前所有登录设备的状态:")
    for auth in authorizations.authorizations:
        # 设备信息
        print(f"设备类型: {auth.device_model}")
        print(f"平台: {auth.platform}")
        print(f"系统版本: {auth.system_version}")
        print(f"IP 地址: {auth.ip}")
        print(f"国家: {auth.country}")

        # 上次访问时间
        # last_active = datetime.datetime.fromtimestamp(auth.date_active)
        # print(f"上次访问时间: {last_active}")

        # 是否为当前设备
        print(f"当前设备: {'是' if auth.current else '否'}")
        print("-" * 40)

async def test1(client: TelegramClient):
    await client.connect()
    # 获取所有会话
    async for dialog in client.iter_dialogs():
        # 输出会话名称和 ID
        print(f"名称: {dialog.name}, ID: {dialog.id}")

        # 判断会话的类型并输出类型
        if isinstance(dialog.entity, User):
            print("类型: 私聊")
        elif isinstance(dialog.entity, Chat):
            print("类型: 群组")
        elif isinstance(dialog.entity, Channel):
            print("类型: 频道")

asyncio.run(main())