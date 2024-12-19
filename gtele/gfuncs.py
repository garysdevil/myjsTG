from telethon import TelegramClient, errors
from telethon.tl.functions.account import GetAuthorizationsRequest, ResetAuthorizationRequest
from tabulate import tabulate
from telethon.tl.functions.channels import JoinChannelRequest
import time

async def list_authorizations(client: TelegramClient):
    """
    获取所有登录状态并以表格形式显示。
    返回一个字典，包含授权 ID 和对应的设备信息。
    """
    authorizations = await client(GetAuthorizationsRequest())

    # 保存授权 ID 和设备信息
    auth_dict = {}

    table_data = []
    for idx, auth in enumerate(authorizations.authorizations):
        auth_id = auth.hash  # 获取授权 ID
        auth_dict[idx] = auth_id  # 索引与授权 ID 映射

        # 添加表格行
        table_data.append([
            idx,  # 序号
            auth_id or "0",
            auth.device_model or "未知设备",  # 设备类型
            auth.platform or "未知平台",  # 平台
            auth.system_version or "未知版本",  # 系统版本
            auth.ip or "未知 IP",  # IP 地址
            auth.country or "未知国家",  # 国家
            auth.date_active.strftime("%Y-%m-%d %H:%M:%S") if auth.date_active else "未知时间",  # 上次访问时间
            "是" if auth.current else "否"  # 当前设备
        ])

    # 打印表格
    headers = ["序号", "auth_id", "设备类型", "平台", "系统版本", "IP 地址", "国家", "上次访问时间", "当前设备"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    return auth_dict

async def kick_authorization(client: TelegramClient, auth_id):
    """
    尝试踢掉指定的登录状态并检查结果。
    """
    try:
        result = await client(ResetAuthorizationRequest(auth_id))
        # 检查操作结果
        if result:
            print(f"已成功踢掉授权 ID 为 {auth_id} 的设备。")
        else:
            print(f"踢掉授权 ID {auth_id} 未成功，可能已经失效或不在登录列表中。")
    except errors.rpcerrorlist.AuthKeyUnregisteredError:
        print(f"授权 ID {auth_id} 未注册或已无效。")
    except errors.rpcerrorlist.FloodWaitError as e:
        print(f"操作频繁，请等待 {e.seconds} 秒后重试。")
    except Exception as e:
        print(f"踢掉设备时出错: {e}")


async def send_message_to_group(client: TelegramClient, group_username: str, message: str):
    """
    向指定的 Telegram 群组发送消息。
    
    参数:
        client (TelegramClient): 已连接的 Telegram 客户端实例
        group_username (str): 群组的用户名或链接
        message (str): 需要发送的消息内容
    """
    try:
        # 获取群组实体
        group = await client.get_entity(group_username)
        
        # 发送消息
        await client.send_message(group, message)
        print(f"消息已成功发送到群组: {group_username}")
    except Exception as e:
        print(f"发送消息失败: {e}")

# 未测试
async def subscribe_channel(client: TelegramClient, target_channel):
    """
    使用提供的 TelegramClient 实例订阅指定频道。

    参数:
        client (TelegramClient): 已经初始化并登录的 Telethon 客户端实例。
        target_channel (str): 要订阅的频道用户名（@username）或邀请链接。
    
    返回:
        dict: 包含订阅结果的字典，包括成功状态和频道信息。
    """
    try:
        # 确保客户端已连接
        if not client.is_connected():
            await client.connect()

        # 检查授权状态
        if not await client.is_user_authorized():
            raise RuntimeError("TelegramClient 未授权，请先登录。")

        # 尝试加入目标频道
        print(f"正在尝试加入频道: {target_channel}")
        result = await client(JoinChannelRequest(target_channel))
        channel_title = result.chats[0].title
        print(f"成功加入频道: {channel_title}")

        return {"status": "success", "channel_title": channel_title}
    
    except errors.UserAlreadyParticipantError:
        # 已经加入频道的情况
        print(f"您已经是频道 {target_channel} 的成员。")
        return {"status": "already_joined", "channel_title": target_channel}
    
    except errors.FloodWaitError as e:
        # 处理 Flood Wait 限制
        print(f"遭遇 Flood Wait 限制，请等待 {e.seconds} 秒后再试。")
        time.sleep(e.seconds)
        return {"status": "flood_wait", "wait_time": e.seconds}
    
    except Exception as e:
        # 捕获其他异常
        print(f"订阅频道时发生错误: {e}")
        return {"status": "error", "error": str(e)}


async def change_password(client: TelegramClient, new_password, old_password=None, hint="My new password hint"):
    """
    更改 Telegram 密码。
    :param client: 已登录的 TelegramClient 实例。
    :param new_password: 要设置的新密码。
    :param old_password: 当前的旧密码（如果需要）。
    :param hint: 新密码的提示。
    """
    try:
        # Telethon 提供的 edit_2fa 方法直接更改密码
        await client.edit_2fa(
            current_password=old_password,  # 如果没有旧密码，请传递 None
            new_password=new_password,     # 新密码
            hint=hint                      # 密码提示
        )
        return "密码已成功更改。"
    except errors.PasswordHashInvalidError:
        return "旧密码不正确，请重试。"
    except Exception as e:
        return f"更改密码时出错: {e}"
