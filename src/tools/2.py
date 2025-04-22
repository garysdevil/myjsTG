import json

# 读取 local/telegram.json 文件
with open("local/telegram.json", "r", encoding="utf-8") as file:
    data = json.load(file)


# # 按指定格式写回文件
# with open('local/telegram.json', 'w', encoding='utf-8') as file:
#     json.dump(data, file, ensure_ascii=False, indent=4)

# 按指定格式写回文件
with open("local/telegram.json", "w", encoding="utf-8") as json_file:
    json_file.write("[\n")  # 开始 JSON 数组
    for seq, item in enumerate(data):
        comma = "" if seq == len(data) - 1 else ","  # 最后一个对象无逗号
        json_file.write(f'{{"seq": {seq + 1},"phone": {item["phone"]},"sessionstr": "{item["sessionstr"]}"}}{comma}\n')
    json_file.write("]")  # 结束 JSON 数组

print("已更新 local/telegram.json 文件")
