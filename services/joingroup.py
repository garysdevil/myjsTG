import asyncio
import re
from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, GetBotCallbackAnswerRequest
from telethon.errors import (
    UserAlreadyParticipantError,
    InviteHashInvalidError,
    InviteHashExpiredError,
    FloodWaitError,
)

class JoinGroup:
    """服务类，用于处理 Telegram 群组加入功能"""

    def __init__(self, client: TelegramClient):
        """
        初始化 JoinGroup 类

        Args:
            client (TelegramClient): 已登录的 Telegram 客户端实例
        """
        self.client = client
        self._is_listening = False  # 标志位，避免重复监听

    async def join(self, invite_link: str) -> str:
        """
        加入群组，不处理验证逻辑。

        Args:
            invite_link (str): 群组邀请链接

        Returns:
            str: 操作结果信息
        """
        return await self._join_group(invite_link)

    async def join_and_verify(self, invite_link: str) -> str:
        """
        加入群组并等待验证消息，处理验证逻辑。

        Args:
            invite_link (str): 群组邀请链接

        Returns:
            str: 操作结果信息
        """
        result = await self._join_group(invite_link)
        if "成功加入群组" in result and not self._is_listening:
            self._is_listening = True
            asyncio.create_task(self._listen_for_verification_messages(invite_link))
        return result

    async def _join_group(self, invite_link: str) -> str:
        """
        内部方法：尝试加入群组并处理可能的错误。

        Args:
            invite_link (str): 群组邀请链接

        Returns:
            str: 操作结果信息
        """
        try:
            # 处理私密邀请链接（例如 https://t.me/+xxx）
            if invite_link.startswith("https://t.me/+"):
                hash_code = invite_link.split("+")[1]  # 提取邀请码
                await self.client(ImportChatInviteRequest(hash_code))
                return f"成功加入群组: {invite_link}"
            # 处理公开链接（例如 https://t.me/Binance_api_Chinese）
            else:
                # 提取 @username 或直接使用链接
                entity = invite_link.split("/")[-1] if invite_link.startswith("https://t.me/") else invite_link
                await self.client(JoinChannelRequest(entity))
                return f"成功加入群组: {invite_link}"
        except UserAlreadyParticipantError:
            return f"您已是群组 {invite_link} 的成员。"
        except InviteHashInvalidError:
            return f"邀请链接无效: {invite_link}"
        except InviteHashExpiredError:
            return f"邀请链接已过期: {invite_link}"
        except FloodWaitError as e:
            return f"操作过于频繁，请等待 {e.seconds} 秒后重试。"
        except Exception as e:
            return f"加入群组失败: {str(e)}"

    async def _handle_verification_message(self, event: events.NewMessage.Event) -> None:
        """
        内部方法：处理群组中的验证消息，自动点击按钮或回复问题。

        Args:
            event (events.NewMessage.Event): 监听到的消息事件
        """
        message = event.message.message
        print(f"收到消息：{message}")  # 调试用，建议替换为日志

        if re.search(r"按钮|button", message):
            print("匹配到点击下方按钮")
            await self._click_verification_button(event)
        elif re.search(r"问题|send", message):
            print("匹配到问题")
            # await self._answer_verification_question(event)
        else:
            print("未识别的消息内容。")

    async def _click_verification_button(self, event: events.NewMessage.Event) -> None:
        """
        内部方法：从事件中提取按钮并发送点击操作。

        Args:
            event (events.NewMessage.Event): 新消息事件
        """
        reply_markup = event.message.reply_markup
        if reply_markup and hasattr(reply_markup, 'rows'):
            for row in reply_markup.rows:
                for button in row.buttons:
                    if hasattr(button, 'data'):
                        print(f"找到按钮: {button.text}")
                        result = await self.client(
                            GetBotCallbackAnswerRequest(
                                peer=event.chat_id,
                                msg_id=event.message.id,
                                data=button.data
                            )
                        )
                        print(f"按钮点击成功，返回结果: {result}")
                        return
        print("未找到符合条件的按钮。")

    async def _answer_verification_question(self, event: events.NewMessage.Event) -> None:
        """
        内部方法：回答验证消息中的问题。

        Args:
            event (events.NewMessage.Event): 监听到的消息事件
        """
        answer = "同意"
        await event.reply(answer)
        print(f"回答问题: {answer}")

    async def _listen_for_verification_messages(self, invite_link: str) -> None:
        """
        内部方法：监听群组消息并处理验证消息。

        Args:
            invite_link (str): 群组邀请链接
        """
        @self.client.on(events.NewMessage)
        async def on_new_message(event):
            if event.chat:
                if event.chat.username in invite_link or str(event.chat.id) in invite_link:
                    print(f"目标群组新消息: {event.chat.username if event.chat.username else event.chat.id}, 内容: {event.message.message}")
                    await self._handle_verification_message(event)
                else:
                    print(f"消息不是来自目标群组: {event.chat.username if event.chat.username else event.chat.id}")
            else:
                print(f"消息不是来自群组: {event.chat.username if event.chat.username else event.chat.id}")

        print(f"开始监听群组 {invite_link} 的验证消息...")
        await self.client.run_until_disconnected()