"""
@Project ：list_ZH_CN
@File    ：test
@Describe：
@Author  ：KlNon
@Date    ：2023/6/26 23:43
"""
from googletrans import Translator

translator = Translator()
translation = translator.translate('wraither', src='en', dest='zh-cn')

print(translation.text)
