# !/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
为什么没有 y, w, yu 几个声母？

声母风格（INITIALS）下，“雨”、“我”、“圆”等汉字返回空字符串，因为根据 《汉语拼音方案》 ， y，w，ü (yu) 都不是声母，在某些特定韵母无声母时，才加上 y 或 w，而 ü 也有其特定规则。 —— @hotoo

如果你觉得这个给你带来了麻烦，那么也请小心一些无声母的汉字（如“啊”、“饿”、“按”、“昂”等）。 这时候你也许需要的是首字母风格（FIRST_LETTER）。 —— @hotoo
"""

from pypinyin import pinyin, lazy_pinyin, Style

pinyinlist = pinyin("西藏", style=Style.NORMAL)
print(pinyinlist)
pinyinlist = pinyin("西藏")
print(pinyinlist)
pinyinlist = pinyin('中心', heteronym=True)  # 启用多音字模式
print(pinyinlist)
pinyinlist = pinyin('银行', heteronym=True)  # 启用多音字模式，无效！！
print(pinyinlist)
pinyinlist = pinyin('武汉', style=Style.FIRST_LETTER)  # 设置拼音风格
print(pinyinlist)
pinyinlist = pinyin("差错")
print(pinyinlist)
pinyinlist = lazy_pinyin('差错')  # 不考虑多音字的情况
print(pinyinlist)
pinyinlist = lazy_pinyin('你好☆☆', errors='ignore')   # 当遇到不包含拼音的字符(串)时，会根据 errors 参数的值做相应的处理:
print(pinyinlist)
pinyinlist = lazy_pinyin('你好☆☆')    # 不做任何处理，原样返回
print(pinyinlist)


