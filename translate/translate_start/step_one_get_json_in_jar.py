"""
@Project ：list_ZH_CN 
@File    ：get_json_in_jar
@Describe：
@Author  ：KlNon
@Date    ：2023/7/8 15:23 
"""
import json
import os
import shutil
import zipfile

from translate.settings import COMPARE_ASSETS_ONE, refresh_json


def get_json_in_jar(gpt_path_word_groups, success_translated_path, jar_dir, output_dir):
    # 删除assets文件夹进行初始化
    shutil.rmtree(COMPARE_ASSETS_ONE)
    # 初始化2个动态json文件,一个机翻列表,1个成功翻译列表
    with open(success_translated_path, 'w', encoding='utf-8-sig') as f:
        json.dump({}, f, ensure_ascii=False, indent=4)
    with open(gpt_path_word_groups, 'w', encoding='utf-8-sig') as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

    refresh_json()
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
                    if name.startswith('assets/') and 'lang/zh_cn.json' in name:
                        # 提取lang/zh_cn.json文件
                        jar_file.extract(name, path=output_dir)
