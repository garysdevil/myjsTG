import asyncio
import logging
from typing import Optional, Dict
import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from config import gconfig  # 假设 config 是你的配置文件模块

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

class TelegramListener:
    """Telegram 客户端监听器类，用于监听消息并提取验证码"""
    
    def __init__(self, api_id: str, api_hash: str, session: str, proxy: Optional[Dict] = None):
        """
        初始化 Telegram 客户端
        
        Args:
            api_id (str): Telegram API ID
            api_hash (str): Telegram API Hash
            session (str): 会话字符串
            proxy (Optional[Dict]): 代理配置字典
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.session = session
        self.proxy = proxy
        self.logger = logging.getLogger(f"local.log")  # 唯一标识客户端
        self.client = self._create_client()

    def _create_client(self) -> TelegramClient:
        """创建 TelegramClient 实例"""
        # 转换代理格式为 Telethon 需要的元组
        proxy_tuple = None
        if self.proxy:
            proxy_tuple = (
                self.proxy["proxy_type"],
                self.proxy["addr"],
                self.proxy["port"],
                self.proxy["rdns"],
                self.proxy["username"],
                self.proxy["password"]
            )
        return TelegramClient(StringSession(self.session), self.api_id, self.api_hash, proxy=proxy_tuple)

    @staticmethod
    def parse_proxy(proxy_str: str) -> Dict:
        """
        解析代理字符串，格式为 'host:port:username:password'
        参考: https://github.com/Anorov/PySocks#usage-1
        
        Args:
            proxy_str (str): 代理字符串
            
        Returns:
            Dict: 代理配置字典
            
        Raises:
            ValueError: 如果代理格式无效
        """
        try:
            parts = proxy_str.split(':')
            if len(parts) != 4:
                raise ValueError("Proxy string must have 4 parts: host:port:username:password")
            host, port, username, password = parts
            return {
                "proxy_type": "socks5",  # 默认 SOCKS5 协议
                "addr": host,
                "port": int(port),
                "rdns": True,  # 默认使用远程 DNS 解析
                "username": username,
                "password": password
            }
        except Exception as e:
            raise ValueError(f"Invalid proxy format: {proxy_str}, error: {str(e)}")

    async def _handle_message(self, event: events.NewMessage.Event) -> None:
        """处理新消息"""
        sender = await event.get_sender()
        message = event.message.message
        self.logger.info(f"收到来自 {sender.username or sender.id} 的消息: {message}")

        # 检查是否为 Telegram 官方消息
        if sender.id in (777000, 42777) or sender.username == "Telegram":
            self.logger.info("收到 Telegram 官方消息")
            match = re.search(r'Login code:\s*(\d{5})', message)
            if match:
                self.logger.info(f"验证码提取成功: {match.group(1)}")
            else:
                self.logger.info("未找到验证码")

    async def start(self) -> None:
        """启动客户端并监听消息"""
        self.logger.info(f"初始化客户端 - api_id: {self.api_id}, session: {self.session[:8]}, proxy: {self.proxy}")
        self.logger.info("正在启动客户端...")

        try:
            await self.client.start()
        except Exception as e:
            self.logger.error(f"客户端启动失败: {str(e)}")
            return

        if not await self.client.is_user_authorized():
            self.logger.warning("用户未授权，请检查 .session 文件或重新登录")
            await self.client.disconnect()
            return

        self.logger.info("客户端已连接，等待接收消息...")
        self.client.add_event_handler(self._handle_message, events.NewMessage())

        try:
            await self.client.run_until_disconnected()
        except Exception as e:
            self.logger.error(f"客户端运行中断: {str(e)}")
        finally:
            await self.client.disconnect()

async def main():
    """主函数"""
    # 从配置文件读取参数
    proxy = TelegramListener.parse_proxy(gconfig.test_proxy)
    listener = TelegramListener(
        api_id=gconfig.account_api_id,
        api_hash=gconfig.account_api_hash,
        session=gconfig.test_sessionstr,
        proxy=proxy
    )
    await listener.start()

if __name__ == "__main__":
    asyncio.run(main())