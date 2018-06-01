# -*- coding=utf-8 -*-
# !/usr/bin/env python

"""
----------------------------------------------
 File Name      :       main
 Description    :
 Author         :       pingz
 Date           :       2018/4/28
----------------------------------------------
"""

__author__ = 'pingz'

import sys
import os
# 跨目录引用模块，把模块所在目录放入sys.path中
sys.path.append(os.path.dirname(os.getcwd())+'\\core\\consume')
import consume1     # pycharm会提示找不到，运行时没问题，不用管
sys.path.append(os.path.dirname(os.getcwd())+'\\core\\product')
import product1

if __name__ == "__main__":
    print("Main.")
    consume1.consume1_func()
    obj = consume1.Cls1()
    print("data =", obj.data)
    obj.test()

