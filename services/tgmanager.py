from typing import Optional, Dict
from telethon import TelegramClient
from telethon.sessions import StringSession

class TGManager:
    """Telegram 客户端管理类，负责创建和管理 TelegramClient 实例"""
    
    def __init__(self, api_id: str, api_hash: str, session: str, proxy: Optional[Dict] = None):
        """
        初始化 TGManager 类
        
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
        self._client = self._create_client()

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

    @property
    def client(self) -> TelegramClient:
        """获取 TelegramClient 实例"""
        return self._client
    
    async def disconnect(self) -> None:
        """断开 TelegramClient 连接"""
        if self._client.is_connected():
            await self._client.disconnect()
            print("TelegramClient 已断开连接")