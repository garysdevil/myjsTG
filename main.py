from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio

from config import gconfig
from utils import gdata
import gtele.gfuncs as gfuncs
from utils import logger

from utils import gutils
from services.tgmanager import TGManager
from services.tglistener import TGListener
from services.joingroup import JoinGroup
import random

logger_tg = logger.get_logger('tg_main', to_console=True)

# 处理登录和操作的函数
async def handle_client_operations(client: TelegramClient):
    invite_link = 'https://t.me/xdag_org'
    try:
        await client.connect()
        result = await JoinGroup(client).join(invite_link)
        return result

        # # 验证是否成功登录
        # me = await client.get_me()
        # logger_tg.info(f"登录成功! 账户名称: {me.username}, 用户 ID: {me.id}")

        # # 示例操作（取消注释以使用）
        # new_password = password
        # old_password = "test"
        # await gfuncs.change_password(client, new_password, old_password)  # 更改2fa密码

        # auth_dict = await gfuncs.list_authorizations(client)  # 获取所有授权设备
        # auth_id_to_kick = auth_dict[100]  # 假设要踢掉第100个设备
        # await gfuncs.kick_authorization(client, auth_id_to_kick)  # 调用提取的函数

        # await gtelethon.send_message_to_group(client, "群名", "现在有什么密码吗")
        # await gjoingroup.join_group_and_verify(client, '群邀请链接')

    finally:
        await client.disconnect()

# 主函数
async def main():
    # 配置参数
    api_id = gconfig.account_api_id
    api_hash = gconfig.account_api_hash
    password = gconfig.account_password  # 两步验证密码（未设置可为空）
    session_str = gconfig.test_sessionstr  # 从配置文件读取的 StringSession
    proxy = gutils.parse_proxy(gconfig.test_proxy)

    # 创建 TGManager 实例
    tg_manager = TGManager(
        api_id=gconfig.account_api_id,
        api_hash=gconfig.account_api_hash,
        session=gconfig.test_sessionstr,
        proxy=proxy
    )
    # listener = TGListener(tg_manager)
    # await listener.start()

    # client = tg_manager.client
    # await handle_client_operations(client)

    data = gdata.get_login_data('local/telegram.json', 'local/proxy.json', 6, 100)
    for item in data:
        seq = item['seq']
        phone = item['phone']
        logger_tg.info(f'{seq}, {phone}')
        session_str = item['sessionstr']
        proxy = gutils.parse_proxy(item['proxy'])
        tg_manager = TGManager(
            api_id=api_id,
            api_hash=api_hash,
            session=session_str,
            proxy=proxy
        )
        client = tg_manager.client
        result = await handle_client_operations(client)
        gutils.write_file('local/joingroup.result',f'{seq}, {phone}, {result}')
        await asyncio.sleep(random.randint(5, 10))

if __name__ == "__main__":
    asyncio.run(main())

