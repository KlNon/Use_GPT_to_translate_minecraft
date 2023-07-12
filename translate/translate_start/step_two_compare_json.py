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
            data1.update(data2)

        keys_diff = set(data1.keys()) ^ set(data2.keys())

        return keys_diff == set(), keys_diff
    except IOError as e:
        print(e)
        return False, None


def compare_assets(asset_path1, asset_path2, results):
    """Compare assets in two paths and merge json files if necessary."""
    for root1, _, files1 in os.walk(asset_path1):
        if EN_JSON in files1:
            root2 = root1.replace(asset_path1, asset_path2)
            en_us_path = os.path.join(root1, EN_JSON)
            zh_cn_path = os.path.join(root2, ZH_JSON)
            if not os.path.exists(zh_cn_path):
                print(f"\n{get_third_last_part(en_us_path)} 没有对应的zh_cn.json文件.")
                results[en_us_path] = False
                continue
            is_same, diff_keys = merge_files(en_us_path, zh_cn_path)
            results[root1] = is_same


def apply_results(results):
    """Apply the results of the comparison by modifying the file system."""
    for file_path, is_same in results.items():
        if is_same:
            del_dir = os.path.dirname(file_path)
            shutil.rmtree(del_dir)
            print(f"{get_third_last_part(file_path)} 经过对比已被完全翻译.")
        else:
            print(f"{get_third_last_part(file_path)} 拥有不完全翻译的条目.")


def compare_all_assets(*compare_assets_paths):
    """Compare all assets in multiple paths."""
    results = {}
    for i in range(len(compare_assets_paths) - 1):
        for j in range(i + 1, len(compare_assets_paths)):
            compare_assets(compare_assets_paths[i], compare_assets_paths[j], results)
    apply_results(results)
