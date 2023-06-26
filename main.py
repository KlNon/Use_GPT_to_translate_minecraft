import json
import os
import re
import zipfile
from googletrans import Translator

import openai

# .jar文件所在的目录
jar_dir = 'E:/FILE/MC/MCs/Minecraft/.minecraft/versions/backup/mods/ZH_CN/扁平化'

# 提取的文件夹要放置的目录
output_dir = 'E:/FILE/MC/MCs/Minecraft/.minecraft/versions/backup/mods/ZH_CN/assets'

# 你的OpenAI API密钥
openai.api_key = ""

# 中英对照表的路径
translation_table_path_words = 'words.json'
translation_table_path_word_groups = 'word_groups.json'

# 谷歌翻译
translator = Translator()

# 是否使用OpenAI
use_openai = False
# 是否手动校准
use_hand = False

# 读取中英对照表
with open(translation_table_path_words, 'r', encoding='utf-8') as f:
    translation_table_words = json.load(f)

with open(translation_table_path_word_groups, 'r', encoding='utf-8') as f:
    translation_table_word_groups = json.load(f)

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
                    # 提取出的文件夹的名字
                    folder_name = name.split('/')[1]

                    # 提取lang/en_us.json文件
                    jar_file.extract(name, path=output_dir)

                    # 读取en_us.json文件
                    with open(os.path.join(output_dir, name), 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # 遍历原始数据的键值对
                    for key in data:
                        words = data[key].split()  # 将value值按空格分割为单词列表

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

                    # 使用中英对照表进行翻译（忽略大小写）,如果没有则使用谷歌翻译进行翻译单词
                    for key in data:
                        words = data[key].split()  # 将value值按空格分割为单词列表
                        for i in range(len(words)):
                            lowercase_word = words[i].lower()  # 将单词转换为小写形式
                            if re.match("^[a-zA-Z]*$", lowercase_word):  # 判断是否全是英文字符
                                if lowercase_word in translation_table_words:
                                    translation = translation_table_words[lowercase_word]
                                    if translation:
                                        words[i] = translation
                                else:
                                    if use_hand:
                                        # 单词不在对照表中，要求用户输入新增的对照表
                                        print(f"单词 '{lowercase_word}' 不在对照表中,其键值对为:{key}:{data[key]}")
                                        new_translation = input("请输入对照英文: ")
                                        if new_translation == "p":
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
                        data[key] = ' '.join(words)  # 将替换后的单词列表重新组合为字符串

                    # 保存更新后的对照表
                    with open(translation_table_path_words, 'w', encoding='utf-8') as f:
                        json.dump(translation_table_words, f, ensure_ascii=False, indent=4)

                    # 选择包含至少一个英文字符的键-值对
                    data_to_translate = {key: val for key, val in data.items() if re.search('[a-zA-Z]', val)}
                    text_to_translate = ",\n".join(data_to_translate.values())

                    # 使用GPT-3进行批量翻译
                    if use_openai:
                        try:
                            response = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system",
                                     "content": "下面我让你来充当Minecraft内容的翻译者，你的目标是把任何语言翻译成中文，翻译要求对于中英文混合的内容,保持其中的中文不变,只翻译其中的翻译英文,例如'诡异 末影人 Death'应将其中的death进行翻译后替换原文,其余不动.其中无法翻译的英文可以保持原文,不要带句号输出格式为:翻译结果A.翻译结果B,翻译结果C..."},
                                    {"role": "user", "content": text_to_translate}
                                ]
                            )
                            translations = response.get("choices")[0]["message"]["content"].strip().replace('\\n',
                                                                                                            '\n').split(
                                ',\n')
                            for key, translation in zip(data_to_translate.keys(), translations):
                                data[key] = translation
                        except Exception as e:
                            print(f"Error during batch translation in file '{name}': {e}")
                            continue

                        # 更新待翻译的文本列表和文本字符串
                        data_to_translate = {key: val for key, val in data.items() if re.search('[a-zA-Z]', val)}
                        text_to_translate = ",\n".join(data_to_translate.values())

                        # 循环遍历data，将值中的空格替换为空字符串
                        for key in data:
                            data[key] = data[key].replace(" ", "")

                        # 将翻译后的内容保存到zh_cn.json文件
                        with open(os.path.join(output_dir, name.replace('en_us.json', 'zh_cn.json')), 'w',
                                  encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=4)

                        print(f'Translated {folder_name} from {filename}')
