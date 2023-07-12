"""
@Project ：list_ZH_CN 
@File    ：find_out_json
@Describe：
@Author  ：KlNon
@Date    ：2023/7/8 15:23 
"""
import json
import os
import re

from collections import Counter


def find_en_us_json(filename, lang_dir, output_dir):
    if filename != 'en_us.json':
        return None

    en_us_json_path = os.path.join(lang_dir, filename)

    # 提取出的文件夹的名字
    folder_name = en_us_json_path.split(os.path.sep)[-3]

    # 读取en_us.json文件
    with open(os.path.join(str(output_dir), str(en_us_json_path)), 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 统计单词频率
    word_counts = Counter()
    for value in data.values():
        # 跳过含有中文的行
        if re.search('[\u4e00-\u9fff]', value):
            continue

        words = re.findall(r'\w+', value.lower())
        if len(words) < 4:
            word_counts.update(words)

    return folder_name, data, en_us_json_path, word_counts
