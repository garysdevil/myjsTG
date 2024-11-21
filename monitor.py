from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio
import re
import os

import gconfig.ginit as ginit

# 主函数
async def main():

    config = ginit.config()
    # 配置参数
    api_id = config['dev']['api_id']  # 替换为您的 API ID
    api_hash = config['dev']['api_hash'] # 替换为您的 API Hash
    key_folder = config['account']['key_folder'] # 保存 Session 文件夹路径

    phone = config['test']['phone'] 
    session_path = get_session_file_path(key_folder, phone)

    # 执行登录监听消息
    await listen_for_code(api_id, api_hash, session_path)

# 获取保存 Session 文件的路径
def get_session_file_path(key_folder, phone):
    """
    获取根据手机号命名的 Session 文件路径
    """
    return os.path.join(key_folder, f"{phone}.session")

# 监听验证码消息
async def listen_for_code(api_id, api_hash, session_path):
    with open(session_path, "r") as file:
        session_str = file.read().strip()

    async with TelegramClient(StringSession(session_str), api_id, api_hash) as client:
        print("正在启动客户端...")

        # 检查授权状态
        if not await client.is_user_authorized():
            print("用户未授权，请检查 .session 文件或重新登录")
            return

        print("客户端已连接，等待接收消息...")

        # 捕获所有消息事件
        @client.on(events.NewMessage)
        async def handle_new_message(event):
            # 获取发送者
            sender = await event.get_sender()
            message = event.message.message
            print(f"收到来自 {sender.username or sender.id} 的消息: {message}")

            # 检查是否来自 Telegram 官方
            if sender.id == 777000 or sender.username == 'Telegram' or sender.id == 42777:
                print("收到 Telegram 官方消息")
                match = re.search(r'Login code:\s*(\d{5})', message)
                if match:
                    print(f"验证码提取成功：{match.group(1)}")
                else:
                    print("未找到验证码")
        # 保持运行直到手动终止
        await client.run_until_disconnected()

# 执行主程序
if __name__ == "__main__":
    asyncio.run(main())
