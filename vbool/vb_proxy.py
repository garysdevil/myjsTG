import json

def read_proxy_file(file_path):
    """
    读取代理文件，返回解析后的代理列表。
    :param file_path: 输入代理文件路径
    :return: 代理数据列表
    """
    try:
        with open(file_path, 'r') as file:
            lines = [line.strip() for line in file if line.strip()]
            proxies = []
            for line in lines:
                parts = line.split(':')
                if len(parts) != 4:
                    raise ValueError(f"代理行格式错误: {line}")
                proxies.append({
                    "host": parts[0],
                    "port": parts[1],
                    "user": parts[2],
                    "pass": parts[3]
                })
            return proxies
    except FileNotFoundError:
        raise FileNotFoundError(f"代理文件 '{file_path}' 未找到。")
    except Exception as e:
        raise RuntimeError(f"读取代理文件时发生错误: {e}")


def generate_json_config(proxies, output_file):
    """
    根据代理列表生成 JSON 配置文件。
    :param proxies: 解析后的代理列表
    :param output_file: 输出 JSON 文件路径
    """
    try:
        config = []
        for idx, proxy in enumerate(proxies, start=1):
            config.append({
                "name": f"aa{idx}",
                "group": "默认分组",
                "proxy": {
                    "mode": 2,
                    "protocol": "SOCKS5",
                    "host": proxy["host"],
                    "port": proxy["port"],
                    "user": proxy["user"],
                    "pass": proxy["pass"]
                },
                "cpu": {"mode": 1, "value": 4},
                "memory": {"mode": 1, "value": 4},
                "homepage": {"mode": 1, "value": "https://web.telegram.org/k/"},
                "os": "Win 11",
                "chrome_version": 124,
                "ua-language": {
                    "mode": 1,
                    "language": "zh-CN",
                    "value": "zh-CN,zh"
                }
            })
        # 写入 JSON 文件
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write("[\n")
            for idx, entry in enumerate(config):
                json_entry = json.dumps(entry, ensure_ascii=False, separators=(",", ":"))
                file.write(f"  {json_entry}")
                file.write(",\n" if idx < len(config) - 1 else "\n")
            file.write("]\n")
        print(f"JSON 配置已成功写入到 {output_file}")
    except Exception as e:
        raise RuntimeError(f"生成 JSON 配置时发生错误: {e}")


def main(input_file, output_file):
    """
    主函数，调用读取和生成配置的函数。
    :param input_file: 输入代理文件路径
    :param output_file: 输出 JSON 文件路径
    """
    try:
        proxies = read_proxy_file(input_file)
        generate_json_config(proxies, output_file)
    except Exception as e:
        print(f"处理过程中发生错误: {e}")


if __name__ == "__main__":
    input_file = "local.vb.proxy"
    output_file = "local.vb.json"
    main(input_file, output_file)

"""
读取local.vb.proxy文件内的代理数据，local.vb.proxy文件内容格式如下:

代理1IP:代理1用户:代理1用户密码
代理2IP:代理2用户:代理2用户密码
"""
"""
输出进local.vb.json文件内，local.vb.json文件格式如下:

[
  {
    "name": "aa1","group": "默认分组",
    "proxy": {"mode": 2,"protocol": "SOCKS5","host": "代理IP","port": "代理端口","user": "代理用户","pass": "代理密码"},
    "cpu": {"mode": 1,"value": 4}, 
    "memory": {"mode": 1,"value": 4}, 
    "homepage": {"mode": 1,"value": "https://web.telegram.org/k/"}, 
    "os": "Win 11","chrome_version": 124,"ua-language": {"mode": 1,"language": "zh-CN","value": "zh-CN,zh"}
  }
]
"""