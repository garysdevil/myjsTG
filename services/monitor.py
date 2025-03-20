from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio
import re
from typing import Optional

def parse_proxy(proxy_str: str) -> dict:
    """
    参考 https://github.com/Anorov/PySocks#usage-1
    解析代理字符串，格式为 'host:port:username:password'
    返回字典格式，适配 set_proxy(proxy_type, addr[, port[, rdns[, username[, password]]]])
    """
    try:
        parts = proxy_str.split(':')
        if len(parts) != 4:
            raise ValueError("Proxy string must have 4 parts: host:port:username:password")
        host, port, username, password = parts
        
        # 返回字典格式
        return {
            "proxy_type": 'socks5',  # 默认 SOCKS5 协议
            "addr": host,
            "port": int(port),
            "rdns": True,  # 默认使用远程 DNS 解析
            "username": username,
            "password": password
        }
    except Exception as e:
        raise ValueError(f"Invalid proxy format: {proxy_str}, error: {str(e)}")
    
async def listen_for_code(api_id: str, api_hash: str, session: str, proxy: Optional[tuple] = None):
    # 显式初始化客户端
    print(f'api_id: {api_id}, api_hash: {api_hash}, sessionstr: {session}, proxy: {proxy}')
    client = TelegramClient(StringSession(session), api_id, api_hash)
    client.set_proxy(proxy)

    print("正在启动客户端...")

    await client.start()  # 启动客户端

    if not await client.is_user_authorized():
        print("用户未授权，请检查 .session 文件或重新登录")
        await client.disconnect()
        return

    print("客户端已连接，等待接收消息...")

    @client.on(events.NewMessage)
    async def handle_new_message(event):
        sender = await event.get_sender()
        message = event.message.message
        print(f"收到来自 {sender.username or sender.id} 的消息: {message}")

        if sender.id == 777000 or sender.username == 'Telegram' or sender.id == 42777:
            print("收到 Telegram 官方消息")
            match = re.search(r'Login code:\s*(\d{5})', message)
            if match:
                print(f"验证码提取成功：{match.group(1)}")
            else:
                print("未找到验证码")

    await client.run_until_disconnected()

# 主函数
async def main():
    from config import gconfig
    proxy = parse_proxy(gconfig.test_proxy)

    await listen_for_code(gconfig.account_api_id, gconfig.account_api_hash, gconfig.test_sessionstr, proxy)

# 执行主程序
if __name__ == "__main__":
    asyncio.run(main())