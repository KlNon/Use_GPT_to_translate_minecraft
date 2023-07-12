import os
import json
import shutil

EN_JSON = 'en_us.json'
ZH_JSON = 'zh_cn.json'


def get_third_last_part(path):
    """Return the third last part of the path."""
    path, _ = os.path.split(path)
    path, _ = os.path.split(path)
    path, third = os.path.split(path)
    return third


def merge_files(file1_path, file2_path):
    """Merge two json files and return the merged result and the keys difference."""
    try:
        with open(file1_path, 'r', encoding='utf-8-sig') as file1, open(file2_path, 'r', encoding='utf-8-sig') as file2:
            data1 = json.load(file1)
            data2 = json.load(file2)
            data1.update(data2)  # 使用 dict.update() 将相同key的替换到en_us.json

        with open(file1_path, 'w', encoding='utf-8') as file1:
            json.dump(data1, file1, ensure_ascii=False, indent=4)

        keys_diff = set(data1.keys()) ^ set(data2.keys())  # Get keys difference

        return keys_diff == set(), keys_diff  # Check if keys are same and return the keys difference
    except IOError as e:
        print(e)
        return False, None


def compare_assets(asset_path1, asset_path2):
    """Compare assets in two paths and merge json files if necessary."""
    for root1, _, files1 in os.walk(asset_path1):
        if EN_JSON in files1:
            root2 = root1.replace(asset_path1, asset_path2)
            en_us_path = os.path.join(root1, EN_JSON)
            zh_cn_path = os.path.join(root2, ZH_JSON)
            if os.path.exists(zh_cn_path):
                is_same, diff_keys = merge_files(en_us_path, zh_cn_path)
                # 如果语言完全被翻译了,则删除当前mod的文件夹
                if is_same:
                    del_dir = os.path.dirname(root1)
                    shutil.rmtree(del_dir)
                    print(f"\n{get_third_last_part(en_us_path)} 经过对比已被完全翻译.")
                else:
                    print(f"\n{get_third_last_part(en_us_path)}---拥有不完全翻译的条目 :{diff_keys}")


def compare_all_assets(compare_assets_one, compare_assets_two, compare_assets_three):
    """Compare all assets in three paths."""
    # 先和自身比(即看自身有无携带zh_cn.json)
    compare_assets(compare_assets_one, compare_assets_one)
    # 再和我自己的材质包比
    compare_assets(compare_assets_one, compare_assets_two)
    # 再和i18n比
    compare_assets(compare_assets_one, compare_assets_three)
