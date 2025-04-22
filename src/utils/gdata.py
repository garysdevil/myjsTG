import json
from typing import List, Dict, Optional
from utils import logger

# 初始化 logger，默认同时输出到文件和控制台
logger = logger.get_logger("bit_log", to_console=True)


def load_json(file_path: str) -> List[Dict]:
    """加载 JSON 文件并返回数据列表"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError(f"File {file_path} must contain a list")
            return data
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {str(e)}")
        raise


def get_login_data(telegram_file: str, proxy_file: str, seq_start: int, seq_end: int) -> List[Dict]:
    """
    根据 seq 范围从 proxy.json 获取 seq 和 proxy，从 telegram.json 获取 phone 和 sessionstr，
    生成新数组。

    Args:
        proxy_file (str): proxy.json 文件路径
        telegram_file (str): telegram.json 文件路径
        seq_start (int): 起始 seq
        seq_end (int): 结束 seq

    Returns:
        List[Dict]: 包含 seq, proxy, phone, sessionstr 的结果列表

    Raises:
        Exception: 如果处理过程中出错
    """
    try:
        # 加载数据
        proxy_data = load_json(proxy_file)
        telegram_data = load_json(telegram_file)

        # 创建 seq 到字段的映射
        proxy_map: Dict[int, Optional[str]] = {item["seq"]: item.get("proxy") for item in proxy_data if "seq" in item}
        telegram_map: Dict[int, Dict] = {
            item["seq"]: {"phone": item.get("phone"), "sessionstr": item.get("sessionstr")}
            for item in telegram_data
            if "seq" in item
        }

        # 组合匹配的数据并检查空字段
        result = []
        for seq in range(seq_start, seq_end + 1):
            if seq in proxy_map and seq in telegram_map:
                proxy = proxy_map[seq]
                phone = telegram_map[seq]["phone"]
                sessionstr = telegram_map[seq]["sessionstr"]

                # 检查并提示空字段
                if proxy is None:
                    logger.warning(f"'proxy' is empty for seq {seq} in {proxy_file}")
                if phone is None:
                    logger.warning(f"'phone' is empty for seq {seq} in {telegram_file}")
                if sessionstr is None:
                    logger.warning(f"'sessionstr' is empty for seq {seq} in {telegram_file}")

                result.append({"seq": seq, "proxy": proxy, "phone": phone, "sessionstr": sessionstr})
            else:
                logger.error(f"No matching data for seq {seq} in one or both files")

        logger.info(f"Processed {len(result)} matching records from seq {seq_start} to {seq_end}")
        return result
    except Exception as e:
        logger.error(f"Error processing Telegram data: {str(e)}")
        raise


def test_get_login_data():
    # 示例文件
    proxy_json = [
        {"seq": 1, "proxy": "46.203.52.111:5722:user1:pass1"},
        {"seq": 2, "proxy": "192.168.1.1:1080:user2:pass2"},
        {"seq": 3, "proxy": None},  # 测试空值
    ]
    telegram_json = [
        {"seq": 1, "phone": "+12345678901", "sessionstr": "session1"},
        {"seq": 2, "phone": "+12345678902", "sessionstr": "session2"},
        {"seq": 3, "phone": None, "sessionstr": "session3"},
    ]

    # 保存到文件
    with open("local/test_proxy.json", "w") as f:
        json.dump(proxy_json, f)
    with open("local/test_telegram.json", "w") as f:
        json.dump(telegram_json, f)

    # 调用函数
    result = get_login_data("telegram.json", "proxy.json", 1, 3)
    for item in result:
        print(item)


# 测试代码
if __name__ == "__main__":
    test_get_login_data()
