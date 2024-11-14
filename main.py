# source ~/devenv/python_tg/bin/activate 
# pip install --upgrade opentele  # pip install PySocks 

from opentele.td import TDesktop
from opentele.tl import TelegramClient
from opentele.api import API, UseCurrentSession, CreateNewSession
import asyncio
import tools
import configparser

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
        'session_new_path': config['telegram']['session_new_path']
    }
    return {'proxy': proxy, 'telegram': telegram}


async def main():
    config = init()
    password = config['telegram']['password']
    
    # 调用函数并打印文件列表
    directory_path = './local.session'  # 替换为你的文件夹路径
    filename_list = tools.list_files_in_directory(directory_path)
    print(filename_list)
    print(config['proxy'])

    filename = filename_list[0]
    sessionPath = r"./local.session/" + filename
    newSessionPath  = r"./local.new.session/" + filename

    client = TelegramClient(newSessionPath)
    client.set_proxy(config['proxy'])
    await client.connect()
    await client.PrintSessions()

    # 生成一个新的 session
    # await generateNewSession(client, newSessionPath, password)

# 测试失败
async def deleteOldSession(sessionPath, seq):
    client = TelegramClient(sessionPath)
    # 踢除之前的设备
    await client.TerminateSession(seq) # 指定设备
    # client.TerminateAllSessions() # 所有设备
  
# 测试失败
async def generateNewSession(client: TelegramClient, newSessionPath, password):
    newAPI = API.TelegramIOS.Generate()
    await client.connect()
    newClient = await client.QRLoginToNewClient(newSessionPath, newAPI, password)
    print(newClient)
    
async def transferSessionToTdata(sessionPath, tdataPath):

    # Load the client from telethon.session file
    # We don't need to specify api, api_id or api_hash, it will use TelegramDesktop API by default.
    client = TelegramClient(sessionPath)
    
    # flag=UseCurrentSession
    #
    # Convert Telethon to TDesktop using the current session.
    tdesk = await client.ToTDesktop(flag=UseCurrentSession)

    # Save the session to a folder named "tdata"
    tdesk.SaveTData(tdataPath)

async def transferTdataToSession(sessionPath, tdataPath):
    # Load TDesktop client from tdata folder
    tdesk = TDesktop(tdataPath)
    
    # Check if we have loaded any accounts
    assert tdesk.isLoaded()

    # flag=UseCurrentSession
    #
    # Convert TDesktop to Telethon using the current session.
    client = await tdesk.ToTelethon(session=sessionPath, flag=UseCurrentSession)


asyncio.run(main())
