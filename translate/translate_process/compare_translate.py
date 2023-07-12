import re
from translate.settings import (
    translation_table_word_groups,
    gpt_word_groups,
    translation_table_words,
    NEED_MANUAL_CONTROL,
    NEED_MANUAL_CONTROL_GROUPS
)
from translate.translate_process.translate_tools import renew_words, save_trans_json, chinese_ratio


def check_and_replace_word_group(data, key, value, word_group, translation_table):
    combined_word = ' '.join(word_group).lower()
    if combined_word in translation_table:
        combined_translation = translation_table[combined_word]
        if combined_translation:
            data[key] = value.replace(combined_word, combined_translation)
            return True
    return False


def generate_word_combinations(words):
    for r in range(2, len(words) + 1):
        for i in range(len(words) - r + 1):
            yield words[i:i + r]


def trans_with_words(data, path, folder_name):
    for key, value in data.items():
        words = value.split()
        # 先对比词组,在对比单词
        for word_group in generate_word_combinations(words):
            if check_and_replace_word_group(data, key, value, word_group, translation_table_word_groups):
                continue
            if check_and_replace_word_group(data, key, value, word_group, gpt_word_groups):
                continue

        # 如果需求翻译的内容超过4个单词,则跳过
        if len(words) > 4:
            continue

        if chinese_ratio(value, 0.5):
            continue

        for i, word in enumerate(words):
            lowercase_word = word.lower()
            if re.match("^[a-zA-Z]*$", lowercase_word):
                if lowercase_word in translation_table_words:
                    translation = translation_table_words[lowercase_word]
                    if translation:
                        words[i] = translation
                else:
                    if NEED_MANUAL_CONTROL:
                        if NEED_MANUAL_CONTROL_GROUPS:
                            handle_group_translation(key, value, data)
                            break
                        handle_word_translation(lowercase_word, key, value, words, i)

        if re.search('[a-zA-Z]', data[key]):
            data[key] = ' '.join(words)

    renew_words()
    save_trans_json(data, path)
    print(f'- Mod:<{folder_name}> 对照翻译结束')


def handle_group_translation(key, value, data):
    print(f"-词组 '{value}' 不在对照表中,其键值对为:{key}:{value}")
    new_translation = input("--请输入完整的翻译: ")
    if new_translation == "":
        print("---跳过所有对照翻译")
    elif new_translation == "p":
        print("---跳过词汇完整对照翻译")
    else:
        translation_table_word_groups[value] = new_translation
        data[key] = new_translation


def handle_word_translation(lowercase_word, key, value, words, i):
    print(f"-单词 '{lowercase_word}' 不在对照表中,其键值对为:{key}:{value}")
    new_translation = input("--请输入对照中文: ")
    if new_translation == "":
        print("---跳过单词对照翻译")
    else:
        translation_table_words[lowercase_word] = new_translation
        words[i] = new_translation
