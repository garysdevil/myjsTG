import asyncio
import re
from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.custom.messagebutton import MessageButton
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from telethon.tl.custom import Button  # 用于处理按钮类型
from telethon.errors import (
    UserAlreadyParticipantError,
    InviteHashInvalidError,
    InviteHashExpiredError,
    FloodWaitError,
)

async def join_group(client: TelegramClient, invite_link: str) -> str:
    """
    尝试加入群组并处理可能的错误。

    Args:
        client (TelegramClient): 已登录的 Telegram 客户端实例
        invite_link (str): 群组的邀请链接

    Returns:
        str: 操作结果信息
    """
    try:
        await client(JoinChannelRequest(invite_link))
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
        return f"加入群组失败: {e}"


async def handle_verification_message(client: TelegramClient, event):
    """
    处理群组中的验证消息，自动点击按钮或回复问题。

    Args:
        event (Event): 监听到的消息事件
    """
    message = event.message.message
    print(f"收到消息：{message}")  # 打印消息以便调试

    # 使用正则表达式匹配消息内容
    # if re.search(r"点击下方按钮", message):
    # 点击下方按钮
    # 下面的按钮
    # button below
    if re.search(r"按钮|button", message):
        print("匹配到点击下方按钮")
        await click_verification_button(client, event)
    elif re.search(r"问题|send", message):
        print("匹配到问题")
        # await answer_verification_question(event)
    else:
        print("未识别的消息内容。")


async def click_verification_button(client: TelegramClient, event):
    """
    从事件中提取按钮并发送点击操作。

    Args:
        client (TelegramClient): Telegram 客户端实例
        event (events.NewMessage.Event): 新消息事件
    """
    reply_markup = event.message.reply_markup  # 获取按钮结构

    if reply_markup and hasattr(reply_markup, 'rows'):  # 检查是否有按钮
        for row in reply_markup.rows:  # 遍历按钮行
            for button in row.buttons:  # 遍历行内按钮
                if hasattr(button, 'data'):  # 确保是回调按钮
                    print(f"找到按钮: {button.text}")
                    # 调用 GetBotCallbackAnswerRequest 执行点击
                    result = await client(
                        GetBotCallbackAnswerRequest(
                            peer=event.chat_id,  # 群组或聊天 ID
                            msg_id=event.message.id,  # 消息 ID
                            data=button.data  # 回调按钮的唯一数据
                        )
                    )
                    print(f"按钮点击成功，返回结果: {result}")
                    return
    print("未找到符合条件的按钮。")

async def answer_verification_question(event):
    """
    方式二 回答验证消息中的问题。

    Args:
        event (Event): 监听到的消息事件
    """
    # 假设问题答案固定为 "同意"
    answer = "同意"
    await event.reply(answer)
    print(f"回答问题: {answer}")


async def listen_for_verification_messages(client: TelegramClient, invite_link: str):
    """
    监听群组消息并处理验证消息。

    Args:
        client (TelegramClient): 已登录的 Telegram 客户端实例
        invite_link (str): 群组邀请链接
    """
    @client.on(events.NewMessage)
    async def on_new_message(event):
        # 检查消息是否来自目标群组
        if event.chat:
            # 如果群组有 username，使用 username 进行匹配
            # 如果群组没有 username，使用群组 ID 进行匹配
            if event.chat.username in invite_link or str(event.chat.id) in invite_link:
                print(f"目标群组新消息: {event.chat.username if event.chat.username else event.chat.id}, 内容: {event.message.message}")
                await handle_verification_message(client, event)
            else:
                print(f"消息不是来自目标群组: {event.chat.username if event.chat.username else event.chat.id}")
        else:
            print(f"消息不是来自群组: {event.chat.username if event.chat.username else event.chat.id}")

    # 保持事件监听
    print(f"开始监听群组 {invite_link} 的验证消息...")
    await client.run_until_disconnected()  # 监听消息，直到断开连接


async def join_group_and_verify(client: TelegramClient, invite_link: str):
    """
    加入群组并监听验证消息。
    
    Args:
        client (TelegramClient): 已登录的 Telegram 客户端实例
        invite_link (str): 群组邀请链接
    """
    result = await join_group(client, invite_link)
    print(result)

    if "成功加入群组" in result:
        # 加入群组后，开始监听验证消息
        await listen_for_verification_messages(client, invite_link)
