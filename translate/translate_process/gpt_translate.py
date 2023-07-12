import re
import openai
from translate.settings import USE_OPENAI, gpt_word_groups
from translate.translate_process.translate_tools import save_trans_json, chinese_ratio


def translate_batch(batch_data, content):
    text_to_translate = "\n".join(batch_data.values())
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": content},
            {"role": "user", "content": text_to_translate}
        ]
    )
    return response


def process_response(response, total_translated_data, data, key_to_index):
    translations = response.get("choices")[0]["message"]["content"].strip().replace('\\n',
                                                                                    '\n').replace(',', '').replace(
        '\n', '!').replace(']]', '\n').split('!')
    usage = response.get('usage')
    total_cost = usage['total_tokens']

    compared_indexes = set()
    for translation in translations:
        translation = translation.replace('<', '').replace('>', '')
        match = re.match(r'(\d+)\^:', translation)
        if match:
            index_of_translation = int(match.group(1))
        else:
            continue  # 如果没有匹配的index，就跳过这个translation
        translation = translation.split('^:', 1)[-1]
        gpt_word_groups[data[key_to_index[index_of_translation]]] = translation
        # 保持第一次翻译的结果,避免重复翻译
        if index_of_translation not in total_translated_data:
            total_translated_data[index_of_translation] = translation
            data[key_to_index[index_of_translation]] = translation
        if index_of_translation not in compared_indexes:
            compared_indexes.add(index_of_translation)
    return total_cost


def trans_with_gpt(data, name, folder_name, auto_control_count):
    # 设置每批的数据数量
    BATCH_SIZE = 50
    total_cost = 0
    complete_translated = False

    if USE_OPENAI:
        print(f'Mod:<{folder_name}> -开始使用GPT进行翻译')

        data_to_translate = {key: val for key, val in data.items() if re.search('[a-zA-Z\u4e00-\u9fff]', val)}

        batch_data = {}
        total_translated_data = {}
        key_to_index = {}

        for index, (key, val) in enumerate(data_to_translate.items(), start=1):

            if chinese_ratio(val, 0.5):
                continue

            if len(val) <= 20 or not chinese_ratio(val, 0.4):
                val = val.replace('\n', ']]')  # 先将换行替换成一个基本不可能在翻译文本中出现的字符,避免出现问题
                batch_data[index] = f"{index}^:{val}"
                key_to_index[index] = key

            # 如果达到批次数量或者是最后一条数据,则进行翻译
            if len(batch_data) == BATCH_SIZE or key == list(data_to_translate.keys())[-1]:
                print(f"--待翻译条目数量{len(batch_data)}")
                if len(batch_data) < BATCH_SIZE:
                    auto_control_count += 1
                    print(f"手动确认计数:{auto_control_count},到达额度时将手动确认是否完毕")

                # 如果批次数据为空或者小于6条,则认为翻译完毕
                if not batch_data or len(batch_data) <= 6:
                    complete_translated = True
                    break

                if batch_data:
                    try:
                        with open('translate/content.txt', 'r', encoding='utf-8') as file:
                            content = file.read()
                        response = translate_batch(batch_data, content)
                        total_cost += process_response(response, total_translated_data, data, key_to_index)
                        batch_data = {}  # Clear for the next batch
                        key_to_index = {}  # Clear for the next batch
                    except Exception as e:
                        print(f"--Error during batch translation in file '{name}': {e}")

    save_trans_json(data, name)
    print(f'---GPT translated |{folder_name}|')
    return total_cost, complete_translated, auto_control_count
