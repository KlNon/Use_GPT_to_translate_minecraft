"""
@Project ：list_ZH_CN
@File    ：test
@Describe：
@Author  ：KlNon
@Date    ：2023/6/26 23:43
"""
from translate.settings import *
from translate.translate_process.translate_tools import *

# remove_files(COMPARE_ASSETS_ONE)
replace_text(COMPARE_ASSETS_ONE, "洋红", "品红")
