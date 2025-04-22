import tomllib

# 读取 TOML 配置文件
try:
    with open("local/config.toml", "rb") as f:
        config = tomllib.load(f)
except FileNotFoundError:
    raise FileNotFoundError("Config file 'local/config.toml' not found")
except tomllib.TOMLDecodeError:
    raise ValueError("Invalid TOML format in 'local/config.toml'")

# 从 account 部分获取配置
account_api_id = config["account"]["api_id"]  # 必须存在
account_api_hash = config["account"]["api_hash"]  # 必须存在
account_password = config["account"].get("password") or None
account_oldpassword = config["account"].get("oldpassword") or None

# 从 task 部分获取配置
task_group_link = config["task"].get("group_link") or None

# 从 test 部分获取配置
test_phone = config["test"].get("phone") or None
test_code_url = config["test"].get("code_url") or None
test_proxy = config["test"].get("proxy") or None
test_sessionstr = config["test"].get("sessionstr") or None
