# Description: Telegram 客户端监听器类，用于监听消息并提取验证码

import re
from telethon import events
from telethon import TelegramClient
from .tgmanager import TGManager
from utils import logger

class TGListener:
    """Telegram 客户端监听器类，用于监听消息并提取验证码"""
    
    def __init__(self, tg_manager: TGManager):
        """
        初始化 TGListener
        
        Args:
            tg_manager (TGClient): TGClient 实例
        """
        self.tg_manager = tg_manager
        # 使用 utils.logger 初始化日志，默认输出到文件和控制台
        self.logger = logger.get_logger('tg_listener', to_console=True)
        self.client = self.tg_manager.client

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
        self.logger.info(f"初始化客户端 - api_id: {self.tg_manager.api_id}, session: {self.tg_manager.session[:8]}, proxy: {self.tg_manager.proxy}")
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