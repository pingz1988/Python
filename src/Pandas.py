# 指定字符集 utf-8
# -*- coding: utf-8 -*-
# 到env设置里查找python的安装路径，再调用对应路径下的解释器程序完成操作
# !/usr/bin/env python

import pandas as pd
import numpy as np

# 通过传递一个list对象来创建一个Series，pandas会默认创建整型索引
s = pd.Series([1, 3, 5, np.nan, 6, 8])
print(s)

# 通过传递一个numpy array，时间索引以及列标签来创建一个DataFrame
dates = pd.date_range("20171108", periods=6)
print(dates)
df = pd.DataFrame(np.random.randn(6,4), index=dates, columns=list('ABCD'))  # random.randn(n,m):返回一个样本，具有标准正态分布
print(df)
# 通过传递一个能够被转换成类似序列结构的字典对象来创建一个DataFrame
