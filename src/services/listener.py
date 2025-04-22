# services/listener.py
import re
import asyncio
from typing import Optional, Dict
from telethon import events, TelegramClient
from .tgmanager import TGManager
from utils import logger


class Listener:
    """Telegram 客户端监听器类，用于监听消息并提取验证码"""

    def __init__(self, tg_manager: TGManager):
        """
        初始化 Listener

        Args:
            tg_manager (TGManager): TGManager 实例
            seq (str): 账号序列号，用于标识
            phone (str): 手机号码，用于标识
        """
        self.tg_manager = tg_manager
        self.seq = tg_manager.seq
        self.phone = tg_manager.phone
        self.logger = logger.get_logger(f"listener_{self.seq}", to_console=True)
        self.client: TelegramClient = self.tg_manager.client
        self._code_queue = asyncio.Queue()  # 每个账号的验证码队列

    async def _handle_message(self, event: events.NewMessage.Event) -> None:
        """处理新消息"""
        sender = await event.get_sender()
        message = event.message.message
        self.logger.info(f"[{self.seq}][{self.phone}] 收到来自 {sender.username or sender.id} 的消息: {message}")

        # 检查是否为 Telegram 官方消息
        if sender.id in (777000, 42777) or sender.username == "Telegram":
            self.logger.info(f"[{self.seq}][{self.phone}] 收到 Telegram 官方消息")
            match = re.search(r"Login code:\s*(\d{5})", message)
            if match:
                code = match.group(1)
                self.logger.info(f"[{self.seq}][{self.phone}] 验证码提取成功: {code}")
                await self._code_queue.put({"seq": self.seq, "phone": self.phone, "code": code})
            else:
                self.logger.info(f"[{self.seq}][{self.phone}] 未找到验证码")

    async def get_code(self, timeout: float = 60.0) -> Optional[Dict[str, str]]:
        """从队列中获取验证码，带超时"""
        try:
            code_data = await asyncio.wait_for(self._code_queue.get(), timeout=timeout)
            return code_data
        except asyncio.TimeoutError:
            self.logger.info(f"[{self.seq}][{self.phone}] 获取验证码超时（{timeout}秒）")
            return None

    async def listen(self) -> None:
        """监听消息"""
        self.client.add_event_handler(self._handle_message, events.NewMessage())
        try:
            self.logger.info(f"[{self.seq}][{self.phone}] 正在监听，接收新信息...")
            await self.client.run_until_disconnected()
        except asyncio.CancelledError:
            self.logger.info(f"[{self.seq}][{self.phone}] 监听任务被取消")
        except Exception as e:
            self.logger.error(f"[{self.seq}][{self.phone}] 客户端运行中断: {str(e)}")
        finally:
            try:
                await self.client.disconnect()
                self.logger.info(f"[{self.seq}][{self.phone}] 客户端已断开连接")
            except Exception as e:
                self.logger.error(f"[{self.seq}][{self.phone}] 断开连接时出错: {str(e)}")
