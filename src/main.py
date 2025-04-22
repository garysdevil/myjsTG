import asyncio

from config import gconfig
from utils import gdata
from utils import logger

from utils import gutils
from services.tgmanager import TGManager
from services.listener import Listener

logger_tg = logger.get_logger("tg_main", to_console=True)


async def test_listen(tg_manager: TGManager):
    try:
        listener = Listener(tg_manager)
        await listener.listen()
    finally:
        await tg_manager.disconnect()


# 主函数
async def main():
    # 配置参数
    api_id = gconfig.account_api_id
    api_hash = gconfig.account_api_hash
    session_str = gconfig.test_sessionstr  # 从配置文件读取的 StringSession
    proxy = gutils.parse_proxy(gconfig.test_proxy)

    # 创建 TGManager 实例
    # tg_manager = TGManager(
    #     api_id=gconfig.account_api_id,
    #     api_hash=gconfig.account_api_hash,
    #     session=gconfig.test_sessionstr,
    #     proxy=proxy
    # )

    data = gdata.get_login_data("local/telegram.json", "local/proxy.json", 601, 700)
    for item in data:
        seq = item["seq"]
        phone = item["phone"]
        logger_tg.info(f"{seq}, {phone}")
        session_str = item["sessionstr"]
        proxy = gutils.parse_proxy(item["proxy"])
        tg_manager = TGManager(api_id=api_id, api_hash=api_hash, session=session_str, proxy=proxy)
        result = await tg_manager.connect()
        if not result[0]:
            gutils.write_file("local/joingroup.result", f"{seq}, {phone}, {result}")
            continue

        # result = await test_join_group(tg_manager)
        # gutils.write_file("local/joingroup.result", f"{seq}, {phone}, {result}")
        # logger_tg.info(f"{seq}, {phone}, {result}")
        # await asyncio.sleep(random.randint(5, 10))


if __name__ == "__main__":
    asyncio.run(main())
