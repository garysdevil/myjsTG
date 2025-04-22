# main.py
import asyncio
from typing import List
from config import gconfig
from utils import gdata, logger, gutils
from services.tgmanager import TGManager
from services.listener import Listener

logger_tg = logger.get_logger("tg_main", to_console=True)


async def main():
    # 配置参数
    api_id = gconfig.account_api_id
    api_hash = gconfig.account_api_hash

    # 获取账号数据
    data = gdata.get_login_data("local/telegram.json", "local/proxy.json", 602, 603)
    listeners: List[Listener] = []  # 添加类型注释
    tasks: List[asyncio.Task[None]] = []  # 添加类型注释

    # 为每个账号创建 TGManager 和 Listener
    for item in data:
        seq = item["seq"]
        phone = item["phone"]
        session_str = item["sessionstr"]
        proxy = gutils.parse_proxy(item["proxy"])
        logger_tg.info(f"初始化账号: {seq}, {phone}")

        # 创建 TGManager，移除重复的 phone 参数
        tg_manager = TGManager(api_id=api_id, api_hash=api_hash, session=session_str, proxy=proxy, phone=phone, seq=seq)

        # 连接客户端
        result = await tg_manager.connect()
        if not result[0]:
            logger_tg.error(f"[{seq}][{phone}] 连接失败: {result}")
            gutils.write_file("local/error.result", f"{seq}, {phone}, {result}")
            continue

        # 创建 Listener，传递 seq 和 phone
        listener = Listener(tg_manager)
        listeners.append(listener)

        # 创建监听任务
        tasks.append(asyncio.create_task(listener.listen()))

    # 同时获取验证码
    async def collect_codes():
        while True:
            for listener in listeners:  # 添加类型注释
                listener: Listener
                code_data = await listener.get_code(timeout=60.0)
                if code_data:
                    logger_tg.info(f"收到验证码: {code_data}")
                    gutils.write_file(
                        "local/codes.result", f"{code_data['seq']}, {code_data['phone']}, {code_data['code']}"
                    )
            await asyncio.sleep(1)  # 避免过于频繁检查

    try:
        # 启动验证码收集任务
        code_task = asyncio.create_task(collect_codes())

        # 等待所有监听任务
        await asyncio.gather(*tasks, return_exceptions=True)
    except KeyboardInterrupt:
        logger_tg.info("收到 Ctrl+C，停止所有监听")
        # 取消所有任务
        for task in tasks:  # 添加类型注释
            task: asyncio.Task[None]
            task.cancel()
        code_task.cancel()
    finally:
        # 确保所有客户端断开连接
        for listener in listeners:  # 添加类型注释
            listener: Listener
            await listener.tg_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
