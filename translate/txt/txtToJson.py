"""
@Project ：list_ZH_CN 
@File    ：txtToJson
@Describe：用于最开始的时候将对照表保存为JSON,现在已经可以不用管了
@Author  ：KlNon
@Date    ：2023/6/26 15:33 
"""
import json

data = {}
name = 'en_cn_entity'

# 读取中英对照表文件
with open(name + '.txt', 'r', encoding='utf-8-sig') as file:
    lines = file.readlines()

# 处理每一行数据
for line in lines:
    line = line.strip()
    if line:
        # 分割中英文文本
        english, chinese = line.split('\t')
        data[english] = chinese

# 将数据转换为 JSON 格式
json_data = json.dumps(data, ensure_ascii=False, indent=4)

# 保存为 JSON 文件
with open(name + '.json', 'w', encoding='utf-8-sig') as file:
    file.write(json_data)
