from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.account import GetAuthorizationsRequest, ResetAuthorizationRequest

from telethon.sync import TelegramClient
from telethon.tl.functions.account import SetAccountTTLRequest
from telethon.tl.types import AccountDaysTTL
import telethon.errors

from tabulate import tabulate
import asyncio

from config import ginit

# 主函数
async def main():
    config = ginit.config()
    # 配置参数
    api_id = config['dev']['api_id']  # 替换为您的 API ID
    api_hash = config['dev']['api_hash']  # 替换为您的 API Hash
    key_path = config['test']['key_path'] 
    key_folder = config['account']['key_folder']  # 保存 key 文件夹路径
    password = config['account']['password']  # 两步验证密码（未设置可为空）
    phone = config['test']['phone']
    code_url = config['test']['code_url'] # 获取验证码的 URL
    proxy = config['test']['proxy']  # 代理地址
    
    # 从文件读取已保存的 StringSession
    with open(key_path, "r") as file:
        session_str = file.read().strip()

    # 使用 StringSession 初始化 TelegramClient
    client = TelegramClient(StringSession(session_str), api_id, api_hash)
    await client.connect()
    # 验证是否成功登录
    me = await client.get_me()
    print(f"登录成功! 账户名称: {me.username}, 用户 ID: {me.id}")
    await list_authorizations(client)

   
# 测试成功
async def list_authorizations(client):
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

# 测试成功
async def kick_authorization(client, auth_id):
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
    except telethon.errors.rpcerrorlist.AuthKeyUnregisteredError:
        print(f"授权 ID {auth_id} 未注册或已无效。")
    except telethon.errors.rpcerrorlist.FloodWaitError as e:
        print(f"操作频繁，请等待 {e.seconds} 秒后重试。")
    except Exception as e:
        print(f"踢掉设备时出错: {e}")

# 测试失败
async def set_inactive_time(client, days=365): 
    """
    设置如果账号非活动时的自毁时间。
    :param client: TelegramClient 对象
    :param days: 自毁天数, 365 表示 1 年
    """
    try:
        # 设置账户非活动自毁时间
        ttl = AccountDaysTTL(days=days)
        await client(SetAccountTTLRequest(ttl))
        print(f"已成功设置 If Inactive For 为 {days} 天。")
    except Exception as e:
        print(f"设置失败: {e}")

asyncio.run(main())