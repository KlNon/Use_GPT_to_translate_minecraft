"""
@Project ：list_ZH_CN 
@File    ：translate_tools
@Describe：
@Author  ：KlNon
@Date    ：2023/7/8 15:20 
"""
import json
import os
import re

from translate.settings import TRANSLATION_TABLE_WORDS_PATH, translation_table_words, \
    TRANSLATION_TABLE_WORD_GROUPS_PATH, translation_table_word_groups, GPT_WORD_GROUPS_PATH, gpt_word_groups, OUTPUT_DIR


def renew_words():
    # 保存更新后的对照表
    with open(TRANSLATION_TABLE_WORDS_PATH, 'w', encoding='utf-8') as f:
        json.dump(translation_table_words, f, ensure_ascii=False, indent=4)
    with open(TRANSLATION_TABLE_WORD_GROUPS_PATH, 'w', encoding='utf-8') as f:
        json.dump(translation_table_word_groups, f, ensure_ascii=False, indent=4)
    with open(GPT_WORD_GROUPS_PATH, 'w', encoding='utf-8') as f:
        json.dump(gpt_word_groups, f, ensure_ascii=False, indent=4)


def del_the_space(data):
    # 循环遍历data，将值中的空格替换为空字符串
    for key in data:
        data[key] = data[key].replace(" ", "")


def save_trans_json(data, path):
    del_the_space(data)
    # 将翻译后的内容保存到zh_cn.json文件
    with open(os.path.join(OUTPUT_DIR, path.replace('en_us.json', 'zh_cn.json')), 'w',
              encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # 保存更新后的数据到en_us.json文件
    with open(os.path.join(OUTPUT_DIR, path), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def save_success(path, data, mod_name, success):
    data[mod_name] = success
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def chinese_ratio(value, limit_ratio):
    total_chars = sum(1 for char in value if re.search('[a-zA-Z\u4e00-\u9fff]', char))
    chinese_chars = sum(1 for char in value if '\u4e00' <= char <= '\u9fff')
    ratio = chinese_chars / total_chars if total_chars > 0 else 0

    if ratio > limit_ratio:  # 如果中文占比超过50%则跳过
        return True
    return False
