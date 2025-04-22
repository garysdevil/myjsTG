# Description: Telegram 客户端监听器类，用于监听消息并提取验证码

import re
from telethon import events
from telethon import TelegramClient
from .tgmanager import TGManager
from utils import logger


class Listener:
    """Telegram 客户端监听器类，用于监听消息并提取验证码"""

    def __init__(self, tg_manager: TGManager):
        """
        初始化 Listener

        Args:
            tg_manager (TGManager): TGManager 实例
        """
        self.tg_manager = tg_manager
        # 使用 utils.logger 初始化日志，默认输出到文件和控制台
        self.logger = logger.get_logger("tg_listener", to_console=True)
        self.client: TelegramClient = self.tg_manager.client

    async def _handle_message(self, event: events.NewMessage.Event) -> None:
        """处理新消息"""
        sender = await event.get_sender()
        message = event.message.message
        self.logger.info(f"收到来自 {sender.username or sender.id} 的消息: {message}")

        # 检查是否为 Telegram 官方消息
        if sender.id in (777000, 42777) or sender.username == "Telegram":
            self.logger.info("收到 Telegram 官方消息")
            match = re.search(r"Login code:\s*(\d{5})", message)
            if match:
                self.logger.info(f"验证码提取成功: {match.group(1)}")
            else:
                self.logger.info("未找到验证码")

    async def listen(self) -> None:
        """监听消息"""
        self.client.add_event_handler(self._handle_message, events.NewMessage())

        try:
            self.logger.info("正在监听，接收新信息...")
            await self.client.run_until_disconnected()
        except Exception as e:
            self.logger.error(f"客户端运行中断: {str(e)}")
        finally:
            try:
                await self.client.disconnect()
                self.logger.info("客户端已断开连接")
            except Exception as e:
                self.logger.error(f"断开连接时出错: {str(e)}")
