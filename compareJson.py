"""
@Project ：list_ZH_CN 
@File    ：compareJson
@Describe：比较有的两个assets,避免重复翻译
@Author  ：KlNon
@Date    ：2023/6/27 2:38 
"""
import os
import json
import shutil


def get_third_last_part(path):
    path, first = os.path.split(path)
    path, second = os.path.split(path)
    path, third = os.path.split(path)
    return third


def merge_files(file1_path, file2_path):
    try:
        with open(file1_path, 'r', encoding='utf-8-sig') as file1, open(file2_path, 'r', encoding='utf-8-sig') as file2:
            data1 = json.load(file1)
            data2 = json.load(file2)
            keys1 = set(data1.keys())
            keys2 = set(data2.keys())
            # 在data1中更新相同的key的value为data2的value
            same_keys = keys1 & keys2  # 获取两个文件中相同的键
            for key in same_keys:
                data1[key] = data2[key]  # 将en_us.json中相同key的value更新为zh_cn.json的value
            with open(file1_path, 'w', encoding='utf-8') as file1:
                json.dump(data1, file1, ensure_ascii=False, indent=4)  # 保存更新后的en_us.json文件

            if keys1 == keys2:
                return True, None
            else:
                return False, keys1 ^ keys2  # 返回键的对称差
    except IOError as e:
        print(e)
        return False, None


def compare_assets(asset_path1, asset_path2):
    for root1, dirs1, files1 in os.walk(asset_path1):
        if 'en_us.json' in files1:
            root2 = root1.replace(asset_path1, asset_path2)
            en_us_path = os.path.join(root1, 'en_us.json')
            zh_cn_path = os.path.join(root2, 'zh_cn.json')
            if os.path.exists(zh_cn_path):
                is_same, diff_keys = merge_files(en_us_path, zh_cn_path)
                if is_same:
                    del_dir = os.path.dirname(root1)
                    shutil.rmtree(del_dir)  # 删除' en_us.json的 lang '文件夹的父级文件夹
                else:
                    print(f"\n{get_third_last_part(en_us_path)}----------have different keys :{diff_keys}")


def compare_all_assets():
    asset_path1 = 'E:/FILE/MC/MCs/Minecraft/.minecraft/versions/backup/mods/ZH_CN/assets/assets'  # 提供您的第一个assets文件夹路径
    asset_path2 = "E:/FILE/MC/MCs/Minecraft/.minecraft/versions/1.19.2-Forge_43.2.14/global_packs/required_resources/KlNon's-Pack/assets"  # 提供您的第二个assets文件夹路径
    asset_path3 = "E:/FILE/MC/MCs/Minecraft/.minecraft/versions/1.19.2-Forge_43.2.14/resourcepacks/Minecraft-Mod-Language-Modpack-Converted-9/assets"
    # 先和自身比(即看自身有无携带zh_cn.json)
    compare_assets(asset_path1, asset_path1)
    # 再和我自己的材质包比
    compare_assets(asset_path1, asset_path2)
    # 再和i18n比
    compare_assets(asset_path1, asset_path3)
