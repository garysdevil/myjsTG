# source ~/devenv/python_tg/bin/activate 
# pip install --upgrade opentele  # pip install PySocks 
# 操作 客户端session文件

from opentele.td import TDesktop
from opentele.tl import TelegramClient
from opentele.api import API, UseCurrentSession, CreateNewSession
import asyncio

import gutils.gutils as gutils
import gconfig.ginit as ginit


async def main():
    config = ginit.config()
    password = config['telegram']['password']
    
    # 调用函数获取文件夹内所有的文件名
    directory_path = config['telegram']['session_folder']  # 替换为你的文件夹路径
    filename_list = gutils.list_files_in_directory(directory_path)

    filename = filename_list[0]
    sessionPath = config['telegram']['session_folder'] + filename
    newSessionPath  = config['telegram']['session_new_folder']  + filename
    client = TelegramClient(sessionPath)
    client.set_proxy(config['proxy'])

    print(filename)
    # print(config['proxy'])
    await client.connect()
    await client.PrintSessions()

    # 生成一个新的 session
    # await generateNewSession(client, newSessionPath, password)

# 测试失败
async def generateNewSession(client: TelegramClient, newSessionPath, password):
    newAPI = API.TelegramIOS.Generate()
    newClient = await client.QRLoginToNewClient(newSessionPath, newAPI, password)
    print(newClient)

# 测试失败
async def deleteOldSession(client: TelegramClient, seq):
    # 踢除之前的设备
    await client.TerminateSession(seq) # 指定设备
    # client.TerminateAllSessions() # 所有设备
    
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
