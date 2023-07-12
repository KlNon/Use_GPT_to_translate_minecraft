"""
@Project ：list_ZH_CN 
@File    ：jsonExtract
@Describe：
@Author  ：KlNon
@Date    ：2023/6/26 23:05 
"""
import json

import json
import re


def extract_and_remove_keys(source_file, target_file):
    # 读取原始JSON文件内容
    with open(source_file, 'r', encoding='utf-8-sig') as f:
        source_data = json.load(f)

    # 创建目标JSON文件的字典对象
    target_data = {}

    # 遍历原始JSON文件的键值对
    for key, value in source_data.items():
        # 使用正则表达式检查键是否由三个或更多单词组成的英文
        if re.match(r'^[a-zA-Z]+(\s[a-zA-Z]+)+$', key):
            # 将键值对添加到目标JSON文件的字典中
            target_data[key] = value

    # 将目标JSON内容写入目标JSON文件
    with open(target_file, 'w', encoding='utf-8-sig') as f:
        json.dump(target_data, f, ensure_ascii=False, indent=4)

    # 删除原始JSON文件中的键值对
    for key in target_data.keys():
        del source_data[key]

    # 将更新后的原始JSON内容写入原始JSON文件
    with open(source_file, 'w', encoding='utf-8-sig') as f:
        json.dump(source_data, f, ensure_ascii=False, indent=4)


# 指定原始JSON文件和目标JSON文件的路径
source_file_path = '../translate/json/other_json/words.json'
target_file_path = '../translate/json/other_json/word_groups.json'

# 调用函数进行处理
extract_and_remove_keys(source_file_path, target_file_path)
