import os
from googletrans import Translator
from collections import Counter

from translate.settings import *
from translate.translate_process.compare_translate import trans_with_words
from translate.translate_process.gpt_translate import trans_with_gpt
from translate.translate_process.translate_tools import save_trans_json, save_success
from translate.translate_start.step_one_get_json_in_jar import get_json_in_jar
from translate.translate_start.step_three_find_out_json import find_en_us_json
from translate.translate_start.step_two_compare_json import compare_all_assets

# 谷歌翻译
translator = Translator()

total_cost = 0
i = 0


def process_directory(path):
    lang_dir = os.path.join(path, 'lang')
    if not os.path.isdir(lang_dir):
        return

    for filename in os.listdir(lang_dir):
        result = find_en_us_json(filename, lang_dir, OUTPUT_DIR)
        if result is not None:
            process_file(result)


def process_file(result):
    global total_cost, i
    i += 1  # 序号
    complete_translated = False
    auto_control_count = 0
    while not complete_translated:
        folder_name, data, path, word_counts = result
        # 如果该模组已经成功翻译，则跳过
        if folder_name in success_translated and success_translated[folder_name]:
            break
        print(f"{i} {folder_name}")
        trans_with_words(data, path, folder_name)
        cost, complete_translated, auto_control_count = trans_with_gpt(data, path, folder_name, auto_control_count)
        total_cost = total_cost + cost

        print(f"-使用的token总数为:{total_cost}")

        # 合并word_counts和high_rate_of_words
        high_rate_of_words.update(word_counts)

        if not complete_translated and auto_control_count > 2:
            new_translation = input(f"启动手动确认模式,模组 '{folder_name}' 是否已经翻译完毕?,按p完毕.")
            if new_translation == "p":
                complete_translated = True
        if complete_translated:
            for data_key, value in data.items():
                data[data_key] = value.replace(' ', '')
            save_trans_json(data, path)
            print(f"模组 '{folder_name}' 翻译完毕.")
            save_success(SUCCESS_TRANSLATED_PATH, success_translated, folder_name, True)


if __name__ == "__main__":
    # 清洗翻译文件,第一次请取消下面两条的注释
    get_json_in_jar(GPT_WORD_GROUPS_PATH, SUCCESS_TRANSLATED_PATH, JAR_DIR, OUTPUT_DIR)
    compare_all_assets(COMPARE_ASSETS_ONE, COMPARE_ASSETS_TWO, COMPARE_ASSETS_THREE)

    high_rate_of_words = Counter()  # 创建空的Counter对象.统计mod中的高频词汇
    translation_table_words_counter = Counter()  # 创建空的Counter对象
    translation_table_words_counter.update(translation_table_words)  # 输入的是对照表中的词
    stack = [OUTPUT_DIR]  # 使用栈来保存待处理的文件夹路径
    while stack:
        current_dir = stack.pop()  # 弹出栈顶的文件夹路径
        process_directory(current_dir)

        # 将子文件夹路径压入栈中
        stack.extend(os.path.join(current_dir, subdir) for subdir in os.listdir(current_dir) if
                     os.path.isdir(os.path.join(current_dir, subdir)))

    # 删除high_rate_of_words中与translation_table_words_counter相同的键
    intersection_keys = set(translation_table_words_counter.keys()) & set(high_rate_of_words.keys())
    for key in intersection_keys:
        if key in high_rate_of_words:
            del high_rate_of_words[key]

    # 输出最终结果
    print(high_rate_of_words)

# TODO 新功能,增加在将en和zh对比的内容制成json,方便长句翻译,如一个mod中的物品翻译了,但句子中该物品仍是英文,那么该长句会在对照翻译中替换该物品的英文
# TODO 替换英文可以用replace试试
