import json
import os
import re
import zipfile
import openai
from googletrans import Translator
from collections import Counter

from compareJson import compare_all_assets

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
use_hand = False
use_hand_word_groups = False

# 读取中英对照表
with open(translation_table_path_words, 'r', encoding='utf-8') as f:
    translation_table_words = json.load(f)

with open(translation_table_path_word_groups, 'r', encoding='utf-8') as f:
    translation_table_word_groups = json.load(f)


def get_language_json_in_jar():
    # 初始化2个动态json文件,一个机翻列表,1个成功翻译列表
    with open(success_translated_path, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=4)
    with open(gpt_path_word_groups, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

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
                        en_file = os.path.join(output_dir, name)  # 获取英文json文件路径

                    if name.startswith('assets/') and 'lang/zh_cn.json' in name:
                        # 提取lang/zh_cn.json文件
                        jar_file.extract(name, path=output_dir)
                        zh_file = os.path.join(output_dir, name)  # 获取中文json文件路径

                    # 比较英文和中文,将已有的中文放入英文文件中,减少汉化工作量
                    with open(en_file, 'r', encoding='utf-8') as en_f, \
                            open(zh_file, 'r', encoding='utf-8') as zh_f:
                        en_dict = json.load(en_f)
                        zh_dict = json.load(zh_f)

                    for key in en_dict.keys():
                        if key in zh_dict:
                            en_dict[key] = zh_dict[key]  # 更新英文文件中的键值对

                    with open(en_file, 'w', encoding='utf-8') as en_f:
                        json.dump(en_dict, en_f, ensure_ascii=False, indent=4)


def find_en_us_json():
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
        # 计算中文占比,占比高的直接跳过
        val = data[key]
        total_chars = sum(1 for char in val if re.search('[a-zA-Z\u4e00-\u9fff]', char))  # 仅计算英文和中文字符的总数
        chinese_chars = sum(1 for char in val if '\u4e00' <= char <= '\u9fff')  # 计算字符串中的中文字符数量
        chinese_ratio = chinese_chars / total_chars if total_chars > 0 else 0  # 计算中文字符占比
        if chinese_ratio > 0.5:
            continue

        words = data[key].split()  # 将value值按空格分割为单词列表
        if len(words) > 4:
            break
        for i in range(len(words)):
            lowercase_word = words[i].lower()  # 将单词转换为小写形式
            if re.match("^[a-zA-Z]*$", lowercase_word):  # 判断是否全是英文字符,是的话判断词组对照表中是否有,否走手动输入
                if lowercase_word in translation_table_words:
                    translation = translation_table_words[lowercase_word]
                    if translation:
                        words[i] = translation
                else:
                    if use_hand:
                        # 首先先整个词组
                        if use_hand_word_groups:
                            print(f"-词组 '{data[key]}' 不在对照表中,其键值对为:{key}:{data[key]}")
                            new_translation = input("--请输入完整的翻译: ")
                            if new_translation == "":
                                print("---跳过所有对照翻译")
                                break
                            if new_translation == "p":
                                print("---跳过词汇完整对照翻译")
                            else:
                                translation_table_word_groups[data[key]] = new_translation
                                data[key] = new_translation
                                break

                        # 单词不在对照表中，要求用户输入新增的对照表
                        print(f"-单词 '{lowercase_word}' 不在对照表中,其键值对为:{key}:{data[key]}")
                        new_translation = input("--请输入对照中文: ")
                        if new_translation == "":
                            print("---跳过单词对照翻译")
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

    print(f'-Translated {folder_name}')


def trans_with_gpt(data, name, folder_name, auto_control_count):
    # 设置每批的数据数量
    BATCH_SIZE = 50
    total_cost = 0
    complete_translated = False

    if use_openai:
        print(f'-Starting GPT translation |{folder_name}|')

        data_to_translate = {key: val for key, val in data.items() if re.search('[a-zA-Z\u4e00-\u9fff]', val)}

        batch_data = {}
        index_to_key = {}
        index = 1
        # 初始化所有翻译过的数据
        total_translated_data = {}

        for key, val in data_to_translate.items():
            total_chars = sum(1 for char in val if re.search('[a-zA-Z\u4e00-\u9fff]', char))
            chinese_chars = sum(1 for char in val if '\u4e00' <= char <= '\u9fff')
            chinese_ratio = chinese_chars / total_chars if total_chars > 0 else 0

            if (total_chars <= 20 or chinese_ratio < 0.4) and chinese_ratio < 0.5:
                val = val.replace('\n', ']]')
                batch_data[key] = f"{index}^:{val}"
                index_to_key[index] = key
                index += 1

            if len(batch_data) == BATCH_SIZE or key == list(data_to_translate.keys())[-1]:
                print(f"--待翻译条目数量{len(batch_data)}")
                text_to_translate = "\n".join(batch_data.values())
                if len(batch_data) < BATCH_SIZE:
                    auto_control_count = auto_control_count + 1
                    print(f"手动确认计数:{auto_control_count},到达额度时将手动确认是否完毕")
                # 如果 batch_data 为空，就跳出循环
                if not batch_data or len(batch_data) <= 6:
                    complete_translated = True
                    break

                if text_to_translate:
                    retry = True
                    file_path = 'content.txt'
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    while retry:
                        try:
                            response = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system",
                                     "content": content},
                                    {"role": "user", "content": text_to_translate}
                                ]
                            )
                            translations = response.get("choices")[0]["message"]["content"].strip().replace('\\n',
                                                                                                            '\n').replace(
                                ',', '').replace('\n', '!').replace(']]', '\n').split('!')
                            usage = response.get('usage')
                            print(
                                f"--Use tokens:{usage['total_tokens']},input tokens:{usage['prompt_tokens']},output tokens:{usage['completion_tokens']}")
                            total_cost += usage['total_tokens']
                            retry = False
                            compared_indexes = set()
                            for key, translation in zip(batch_data.keys(), translations):
                                translation = translation.replace('<', '').replace('>', '')
                                match = re.match(r'(\d+)\^:', translation)
                                if match:
                                    index_of_translation = int(match.group(1))
                                else:
                                    index = int(translation.split('^:', 1)[0].strip())
                                translation = translation.split('^:', 1)[-1]
                                gpt_word_groups[data[index_to_key[index_of_translation]]] = translation
                                # 保持第一次翻译的结果,避免重复翻译
                                if key not in total_translated_data:
                                    total_translated_data[index_to_key[index_of_translation]] = translation
                                    data[index_to_key[index_of_translation]] = translation
                                if index_of_translation not in compared_indexes:
                                    compared_indexes.add(index_of_translation)
                                    del index_to_key[index_of_translation]
                            for index_of_translation in index_to_key.keys():
                                data[index_to_key[index_of_translation]] = ""
                        except Exception as e:
                            print(f"--Error during batch translation in file '{name}': {e}")
                batch_data = {}  # Clear for the next batch
                index_to_key = {}  # Clear for the next batch
                index = 1  # Reset for the next batch

    save_trans_json(data, name)
    print(f'---GPT translated |{folder_name}|')
    return total_cost, complete_translated, auto_control_count


if __name__ == "__main__":
    cost = 0
    total_cost = 0
    # 清洗翻译文件
    get_language_json_in_jar()
    compare_all_assets()

    with open(gpt_path_word_groups, 'r', encoding='utf-8') as f:
        gpt_word_groups = json.load(f)

    with open(success_translated_path, 'r', encoding='utf-8') as f:
        success_translated = json.load(f)

    high_rate_of_words = Counter()  # 创建空的Counter对象
    translation_table_words_counter = Counter()  # 创建空的Counter对象
    translation_table_words_counter.update(translation_table_words)
    i = 0
    stack = [output_dir]  # 使用栈来保存待处理的文件夹路径
    while stack:
        current_dir = stack.pop()  # 弹出栈顶的文件夹路径
        lang_dir = os.path.join(current_dir, 'lang')
        complete_translated = False
        need_manual_control = False
        auto_control_count = 0
        if os.path.isdir(lang_dir):
            i = i + 1
            for filename in os.listdir(lang_dir):
                result = find_en_us_json()
                if result is not None:
                    while not complete_translated:
                        folder_name, data, name, word_counts = result
                        # 如果该模组已经成功翻译，则跳过
                        if folder_name in success_translated and success_translated[folder_name]:
                            break
                        print(f"{i} {folder_name}")
                        trans_with_words(data, name, folder_name)
                        cost, complete_translated,auto_control_count = trans_with_gpt(data, name, folder_name, auto_control_count)
                        total_cost = total_cost + cost

                        print(f"-Use all tokens:{total_cost}")

                        # 合并word_counts和high_rate_of_words
                        high_rate_of_words.update(word_counts)

                        if not complete_translated and auto_control_count > 2:
                            new_translation = input(f"启动手动确认模式,模组 '{folder_name}' 是否已经翻译完毕?,按p完毕.")
                            if new_translation == "p":
                                complete_translated = True
                        if complete_translated:
                            for key, value in data.items():
                                data[key] = value.replace(' ', '')
                            save_trans_json(data, name)
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
