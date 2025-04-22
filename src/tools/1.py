"""
模块：session_to_json.py
功能：读取 ./keys.000_100 文件夹内的 .session 文件，生成 JSON 格式输出。
输入：文件夹 ./keys.000_100 内的文件，文件名格式为 <phone>.session，例如 12053018273.session。
输出：JSON 文件 ./keys.000_100.json，每行一个对象，包含 phone 和 sessionstr。
"""

import os


def process_session_files(folder_path: str, output_path: str) -> None:
    """
    处理文件夹内的 .session 文件，生成 JSON 输出。

    Args:
        folder_path (str): 输入文件夹路径，例如 './keys.000_100'
        output_path (str): 输出 JSON 文件路径，例如 './keys.000_100.json'

    Raises:
        FileNotFoundError: 文件夹不存在时抛出
        ValueError: 文件名格式错误时抛出
    """
    # 检查文件夹是否存在
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"文件夹未找到: {folder_path}")

    # 获取所有 .session 文件
    session_files = [f for f in os.listdir(folder_path) if f.endswith(".session")]
    if not session_files:
        print(f"警告：{folder_path} 中未找到 .session 文件")
        return

    # 存储结果
    result = []

    # 处理每个文件
    for filename in session_files:
        file_path = os.path.join(folder_path, filename)
        try:
            # 从文件名提取 phone（移除 .session 后缀）
            phone_str = filename.replace(".session", "")
            phone = int(phone_str)  # 转换为整数
        except ValueError:
            raise ValueError(f"文件名格式错误，无法解析 phone: {filename}")

        # 读取文件内容
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                sessionstr = file.read().strip()  # 读取内容并移除首尾空白
        except Exception as e:
            print(f"警告：读取文件 {file_path} 失败，已跳过: {e}")
            continue

        # 添加到结果
        result.append({"phone": phone, "sessionstr": sessionstr})

    # 写入 JSON 文件
    with open(output_path, "w", encoding="utf-8") as json_file:
        json_file.write("[\n")  # 开始 JSON 数组
        for seq, item in enumerate(result):
            comma = "" if seq == len(result) - 1 else ","  # 最后一个对象无逗号
            json_file.write(f'{{"seq": {seq},"phone": {item["phone"]},"sessionstr": "{item["sessionstr"]}"}}{comma}\n')
        json_file.write("]")  # 结束 JSON 数组


def main():
    """主函数：执行文件处理并生成 JSON"""
    folder_path = "local/allkeys/all"
    output_path = "tools/local/stringkey.json"

    try:
        process_session_files(folder_path, output_path)
        print(f"成功：已生成 {output_path}")
    except Exception as e:
        print(f"失败：{e}")


if __name__ == "__main__":
    main()
