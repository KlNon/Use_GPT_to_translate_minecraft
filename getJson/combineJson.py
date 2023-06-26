"""
@Project ：list_ZH_CN 
@File    ：combineJson
@Describe：
@Author  ：KlNon
@Date    ：2023/6/26 20:00 
"""
import os
import json
import glob


def merge_json_files(directory, output_filename):
    # 初始化一个空字典来保存合并的数据
    merged_data = {}

    # 遍历目录中的所有.json文件
    for filename in glob.glob(os.path.join(directory, '*.json')):
        with open(filename, 'r', encoding='utf-8') as f:
            # 加载当前文件的数据
            data = json.load(f)

            # 遍历当前文件的所有键
            for key in data.keys():
                # 如果键还没有在合并的数据中出现过，那么添加它
                if key not in merged_data:
                    merged_data[key.lower()] = data[key]

    # 将合并的数据写入到输出文件
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)


# 使用函数
merge_json_files('E:/MyPythonJob/list_ZH_CN/getJson', '../words.json')
