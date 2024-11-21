import json

def extract_data(line):
    """
    从每一行提取 phone, code_url, proxy 信息，并格式化 Proxy
    """
    parts = line.split()

    # 检查基本字段数量是否符合要求
    if len(parts) < 2:
        print("分割后的结果不足2个部分, 检查输入数据。")
        return None

    phone = parts[0]
    code_url = parts[1]
    proxy = None  # 默认值为 None

    # 如果提供了代理信息，尝试解析
    if len(parts) >= 3:
        proxy_raw = parts[2]
        proxy_parts = proxy_raw.split(':')
        if len(proxy_parts) == 4:
            host, port, username, password = proxy_parts
            proxy = f"socks5://{username}:{password}@{host}:{port}"
        else:
            print(f"Proxy 格式不正确: {proxy_raw}")

    return {"phone": phone, "code_url": code_url, "proxy": proxy}

def process_file(file_path):
    """
    处理文件，提取每行的 phone, code_url 和 proxy 信息，并附加序号
    """
    result = []
    
    with open(file_path, 'r') as file:
        for index, line in enumerate(file, start=1):
            data = extract_data(line)
            if data:
                # 添加序号到结果
                data["index"] = index
                result.append(data)
    
    return result

def get_extracted_data(file_path):
    """
    对外暴露的接口：提取文件中的数据并返回 JSON 结构
    """
    data = process_file(file_path)
    return json.dumps(data, indent=4, ensure_ascii=False)  # 返回格式化的 JSON 字符串

if __name__ == "__main__":
    # 文件路径
    file_path = 'local/data.txt'  # 请确保文件路径正确

    # 获取 JSON 数据并打印
    json_data = get_extracted_data(file_path)
    print(json_data)


'''
输入文件路径
get_extracted_data(file_path)

假设文件中的一行数据如下：
12345678901 https://example.com/code 192.168.1.1:8080:username:password
98765432100 https://example.com/code2 192.168.1.2:8081:user2:pass2


返回的 JSON 格式字符串如下：
[
    {
        "phone": "12345678901",
        "code_url": "https://example.com/code",
        "proxy": "socks5://username:password@192.168.1.1:8080",
        "index": 1
    },
    {
        "phone": "98765432100",
        "code_url": "https://example.com/code2",
        "proxy": "socks5://user2:pass2@192.168.1.2:8081",
        "index": 2
    }
]
'''