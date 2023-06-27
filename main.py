import json
import os
import re
import zipfile
import openai
from googletrans import Translator
from collections import Counter

from compareJson import compare_assets, compare_all_assets

# .jar文件所在的目录
jar_dir = 'E:/FILE/MC/MCs/Minecraft/.minecraft/versions/backup/mods/ZH_CN/扁平化'

# 提取的文件夹要放置的目录
output_dir = 'E:/FILE/MC/MCs/Minecraft/.minecraft/versions/backup/mods/ZH_CN/assets'

# 你的OpenAI API密钥
openai.api_key = ""

# 中英对照表的路径
translation_table_path_words = 'words.json'
translation_table_path_word_groups = 'word_groups.json'
gpt_path_word_groups = 'gpt_groups.json'
success_translated_path = 'success_translated.json'
# 谷歌翻译
translator = Translator()

# 是否使用OpenAI
use_openai = True
# 是否手动校准
use_hand = True
use_hand_word_groups = True

# 读取中英对照表
with open(translation_table_path_words, 'r', encoding='utf-8') as f:
    translation_table_words = json.load(f)

with open(translation_table_path_word_groups, 'r', encoding='utf-8') as f:
    translation_table_word_groups = json.load(f)

with open(gpt_path_word_groups, 'r', encoding='utf-8') as f:
    gpt_word_groups = json.load(f)

with open(success_translated_path, 'r', encoding='utf-8') as f:
    success_translated = json.load(f)


def get_en_us_json_in_jar():
    # 遍历.jar文件所在的目录
    for filename in os.listdir(jar_dir):
        if filename.endswith(".jar"):
            jar_path = os.path.join(jar_dir, filename)

            # 打开.jar文件
            with zipfile.ZipFile(jar_path, 'r') as jar_file:
                # 查看.jar文件中的内容
                for name in jar_file.namelist():
                    # 如果是assets文件夹下的文件夹并且包含lang/en_us.json文件
                    if name.startswith('assets/') and 'lang/en_us.json' in name:
                        # 提取lang/en_us.json文件
                        jar_file.extract(name, path=output_dir)


def find_en_us_json(stack):
    if filename == 'en_us.json':
        en_us_json_path = os.path.join(lang_dir, filename)
        # 读取en_us.json文件

        # 提取出的文件夹的名字
        folder_name = en_us_json_path.split(os.path.sep)[-3]
        with open(os.path.join(str(output_dir), str(en_us_json_path)), 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 统计单词频率

        word_counts = Counter()
        for value in data.values():
            words = re.findall(r'\w+', value.lower())
            if len(words) < 4:
                words_without_chinese = [word for word in words if not re.search('[\u4e00-\u9fff]', word)]
                word_counts.update(words_without_chinese)

        return folder_name, data, en_us_json_path, word_counts

    return None


def renew_words():
    # 保存更新后的对照表
    with open(translation_table_path_words, 'w', encoding='utf-8') as f:
        json.dump(translation_table_words, f, ensure_ascii=False, indent=4)
    with open(translation_table_path_word_groups, 'w', encoding='utf-8') as f:
        json.dump(translation_table_word_groups, f, ensure_ascii=False, indent=4)
    with open(gpt_path_word_groups, 'w', encoding='utf-8') as f:
        json.dump(gpt_word_groups, f, ensure_ascii=False, indent=4)


def del_the_space(data):
    # 循环遍历data，将值中的空格替换为空字符串
    for key in data:
        data[key] = data[key].replace(" ", "")


def save_trans_json(data, name):
    # 将翻译后的内容保存到zh_cn.json文件
    with open(os.path.join(output_dir, name.replace('en_us.json', 'zh_cn.json')), 'w',
              encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # 保存更新后的数据到en_us.json文件
    with open(os.path.join(output_dir, name), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def trans_with_words(data, name, folder_name):
    # 遍历原始数据的键值对
    for key in data:
        words = data[key].split()  # 将value值按空格分割为单词列表

        # 词组对照
        # 生成所有可能的排列组合
        for r in range(2, len(words) + 1):  # 按照2个及以上的长度进行排列组合
            for i in range(len(words) - r + 1):
                combination = words[i:i + r]
                combined_word = ' '.join(combination)

                # 检查整个词组是否存在于中英对照表中
                if combined_word.lower() in translation_table_word_groups:
                    combined_translation = translation_table_word_groups[combined_word.lower()]
                    if combined_translation:
                        data[key] = data[key].replace(combined_word, combined_translation)
                        continue
                # 若不在词组对照表中,则对比词组是否在机翻对照表中
                if combined_word.lower() in gpt_word_groups:
                    combined_translation = gpt_word_groups[combined_word.lower()]
                    if combined_translation:
                        data[key] = data[key].replace(combined_word, combined_translation)
                        continue

    # 单词对照
    # 使用中英对照表进行翻译（忽略大小写）,如果没有则使用谷歌翻译进行翻译单词
    for key in data:
        words = data[key].split()  # 将value值按空格分割为单词列表
        if len(words) > 4:
            break
        for i in range(len(words)):
            lowercase_word = words[i].lower()  # 将单词转换为小写形式
            if re.match("^[a-zA-Z]*$", lowercase_word):  # 判断是否全是英文字符
                if lowercase_word in translation_table_words:
                    translation = translation_table_words[lowercase_word]
                    if translation:
                        words[i] = translation
                else:
                    if use_hand:
                        # 首先先整个词组
                        if use_hand_word_groups:
                            print(f"词组 '{data[key]}' 不在对照表中,其键值对为:{key}:{data[key]}")
                            new_translation = input("请输入完整的翻译: ")
                            if new_translation == "":
                                print("跳过所有翻译")
                                break
                            if new_translation == "p":
                                print("跳过完整翻译")
                            else:
                                translation_table_word_groups[data[key]] = new_translation
                                data[key] = new_translation
                                break

                        # 单词不在对照表中，要求用户输入新增的对照表
                        print(f"单词 '{lowercase_word}' 不在对照表中,其键值对为:{key}:{data[key]}")
                        new_translation = input("请输入对照中文: ")
                        if new_translation == "":
                            print("跳过")
                            continue
                        translation_table_words[lowercase_word] = new_translation
                        words[i] = new_translation
                #         谷歌翻译(效果不佳)
                # else:
                #     try:
                #         translation = translator.translate(lowercase_word, dest='zh-cn')
                #         if translation:
                #             words[i] = translation.text
                #     except Exception as e:
                #         print(f"Error during translation of '{lowercase_word}' in file '{name}': {e}")
                #         continue
            else:
                continue  # 如果不是全英文字符，则跳过

        if re.search('[a-zA-Z]', data[key]):
            data[key] = ' '.join(words)  # 将替换后的单词列表重新组合为字符串

    renew_words()

    save_trans_json(data, name)

    print(f'Translated {folder_name}')


def trans_with_gpt(data, name, folder_name):
    # 使用中英对照表进行翻译（忽略大小写）,如果没有则使用谷歌翻译进行翻译单词
    # 使用GPT-3进行批量翻译
    total_cost = 0
    if use_openai:
        print(f'Start GPT translating |{folder_name}|')
        # 选择包含至少一个英文字符的键-值对
        data_to_translate = {key: val for key, val in data.items() if re.search('[a-zA-Z]', val)}
        text_to_translate = "\n".join(data_to_translate.values())
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",
                     "content": "下面我让你来充当Minecraft内容的翻译者，你的目标是把任何语言翻译成中文，翻译要求对于中英文混合的内容,保持其中的中文不变,只翻译其中的翻译英文,例如'诡异 末影人 Death'应将其中的death进行翻译后替换原文,其余不动.其中无法翻译的英文可以保持原文,不要带句号输出格式为:翻译结果A.翻译结果B,翻译结果C..."},
                    {"role": "user", "content": text_to_translate}
                ]
            )
            translations = response.get("choices")[0]["message"]["content"].strip().replace('\\n', '\n').replace(',',
                                                                                                                 '').split(
                '\n')
            usage = response.get('usage')
            print(
                f"Use tokens:{usage['total_tokens']},input tokens:{usage['prompt_tokens']},output tokens:{usage['completion_tokens']}")
            for key, translation in zip(data_to_translate.keys(), translations):
                gpt_word_groups[data[key]] = translation
                data[key] = translation
        except Exception as e:
            print(f"Error during batch translation in file '{name}': {e}")

    save_trans_json(data, name)

    print(f'GPT translated |{folder_name}|')
    return total_cost


if __name__ == "__main__":
    cost = 0
    # 清洗翻译文件
    # get_en_us_json_in_jar()
    # compare_all_assets()

    high_rate_of_words = Counter()  # 创建空的Counter对象
    translation_table_words_counter = Counter()  # 创建空的Counter对象
    translation_table_words_counter.update(translation_table_words)
    i = 0
    stack = [output_dir]  # 使用栈来保存待处理的文件夹路径
    while stack:
        current_dir = stack.pop()  # 弹出栈顶的文件夹路径
        lang_dir = os.path.join(current_dir, 'lang')
        if os.path.isdir(lang_dir):
            for filename in os.listdir(lang_dir):
                result = find_en_us_json(stack)
                if result is not None:
                    i = i + 1
                    folder_name, data, name, word_counts = result
                    # 如果该模组已经成功翻译，则跳过
                    if folder_name in success_translated and success_translated[folder_name] is not None:
                        continue
                    print(f"{i} {folder_name}")
                    trans_with_words(data, name, folder_name)
                    cost = cost + trans_with_gpt(data, name, folder_name)

                    print(
                        f"Use all tokens:{cost}")

                    # 合并word_counts和high_rate_of_words
                    high_rate_of_words.update(word_counts)

                    new_translation = input(f"模组 '{folder_name}' 是否已经翻译完毕?,按回车完毕.")
                    if new_translation == "":
                        print(f"模组 '{folder_name}' 翻译完毕.")
                        success_translated[folder_name] = True
                        with open(success_translated_path, 'w', encoding='utf-8') as f:
                            json.dump(success_translated, f, ensure_ascii=False, indent=4)
                        continue
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
