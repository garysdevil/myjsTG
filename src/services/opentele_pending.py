# source ~/devenv/python_tg/bin/activate
# pip install --upgrade opentele  # pip install PySocks
# 操作 客户端session文件

from opentele.td import TDesktop
from opentele.tl import TelegramClient
from opentele.api import API, UseCurrentSession
import asyncio

import utils.gutils as gutils
from config import gconfig


async def main():
    # password = gconfig.account_password

    # 调用函数获取文件夹内所有的文件名
    session_folder = "../local/sessions"  # 替换为你的文件夹路径
    # session_folder_new = '../local/newsessions'
    filename_list = gutils.list_files_in_directory(session_folder)

    filename = filename_list[0]
    sessionPath = session_folder + filename
    # newSessionPath = session_folder_new + filename
    client = TelegramClient(sessionPath)
    client.set_proxy(gconfig.test_proxy)

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
    await client.TerminateSession(seq)  # 指定设备
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
    await tdesk.ToTelethon(session=sessionPath, flag=UseCurrentSession)


asyncio.run(main())
