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
    with open(TRANSLATION_TABLE_WORDS_PATH, 'w', encoding='utf-8-sig') as f:
        json.dump(translation_table_words, f, ensure_ascii=False, indent=4)
    with open(TRANSLATION_TABLE_WORD_GROUPS_PATH, 'w', encoding='utf-8-sig') as f:
        json.dump(translation_table_word_groups, f, ensure_ascii=False, indent=4)
    with open(GPT_WORD_GROUPS_PATH, 'w', encoding='utf-8-sig') as f:
        json.dump(gpt_word_groups, f, ensure_ascii=False, indent=4)


def del_the_space(data):
    # 循环遍历data，将值中的空格替换为空字符串
    for key in data:
        if chinese_ratio(data[key], 0.6):
            data[key] = data[key].replace(" ", "")


def save_trans_json(data, path):
    del_the_space(data)
    # 将翻译后的内容保存到zh_cn.json文件
    with open(os.path.join(OUTPUT_DIR, path.replace('en_us.json', 'zh_cn.json')), 'w',
              encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # 保存更新后的数据到en_us.json文件
    with open(os.path.join(OUTPUT_DIR, path), 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def save_success(path, data, mod_name, success):
    data[mod_name] = success
    with open(path, 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def chinese_ratio(value, limit_ratio):
    total_chars = sum(1 for char in value if re.search('[a-zA-Z\u4e00-\u9fff]', char))
    chinese_chars = sum(1 for char in value if '\u4e00' <= char <= '\u9fff')
    ratio = chinese_chars / total_chars if total_chars > 0 else 0

    if ratio > limit_ratio:  # 如果中文占比超过比例
        return True
    return False


def remove_files(path):
    for root, dirs, files in os.walk(path):
        if 'en_us.json' in files:
            try:
                os.remove(os.path.join(root, 'en_us.json'))
                print(f"成功删除文件：{os.path.join(root, 'en_us.json')}")
            except Exception as e:
                print(f"无法删除文件：{os.path.join(root, 'en_us.json')}")
                print(f"错误信息：{e}")
        for dir_inside in dirs:
            remove_files(dir_inside)


def replace_text(path, original_text, new_text):
    for root, dirs, files in os.walk(path):
        if 'zh_cn.json' in files:
            try:
                with open(os.path.join(root, 'zh_cn.json'), 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                # 假设 data 是一个字典，我们将遍历它的所有键值对
                for key in data:
                    if isinstance(data[key], str):  # 确保值是一个字符串，然后进行替换
                        data[key] = data[key].replace(original_text, new_text)
                with open(os.path.join(root, 'zh_cn.json'), 'w', encoding='utf-8-sig') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"成功替换文字在文件：{os.path.join(root, 'zh_cn.json')}")
            except Exception as e:
                print(f"无法替换文字在文件：{os.path.join(root, 'zh_cn.json')}")
                print(f"错误信息：{e}")
        for dir_inside in dirs:
            replace_text(dir_inside, original_text, new_text)
