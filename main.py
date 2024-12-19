from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio

from gconfig import ginit
import gtele.gfuncs as gfuncs
import gtele.gjoingroup as gjoingroup

# 主函数
async def main():
    config = ginit.config()
    # 配置参数
    api_id = config['dev']['api_id']  # 替换为您的 API ID
    api_hash = config['dev']['api_hash']  # 替换为您的 API Hash
    key_path = config['test']['key_path'] 
    # key_folder = config['account']['key_folder']  # 保存 key 文件夹路径
    password = config['account']['password']  # 两步验证密码（未设置可为空）
    # phone = config['test']['phone']
    # code_url = config['test']['code_url'] # 获取验证码的 URL
    # proxy = config['test']['proxy']  # 代理地址
    
    # 从文件读取已保存的 StringSession
    with open(key_path, "r") as file:
        session_str = file.read().strip()

    # 使用 StringSession 初始化 TelegramClient
    client = TelegramClient(StringSession(session_str), api_id, api_hash)
    try:
        await client.connect()
        # 验证是否成功登录
        me = await client.get_me()
        print(f"登录成功! 账户名称: {me.username}, 用户 ID: {me.id}")
        print(key_path)
        print(password)

        # new_password = password
        # old_password = "test"
        # await gfuncs.change_password(client, new_password, old_password) # 更改2fa密码

        # auth_dict = await gfuncs.list_authorizations(client)  # 获取所有授权设备
        # auth_id_to_kick = auth_dict[100]  # 假设要踢掉第100个设备
        # await gfuncs.kick_authorization(client, auth_id_to_kick)  # 调用提取的函数

        # await gtelethon.send_message_to_group(client, "群名", "现在有什么密码吗")
        # await gjoingroup.join_group_and_verify(client, '群邀请链接')

    finally:
        await client.disconnect()

asyncio.run(main())