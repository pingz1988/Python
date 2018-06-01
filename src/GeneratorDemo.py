# -*- coding=utf-8 -*-
# !/usr/bin/env python

"""
----------------------------------------------
 File Name      :       generator_use
 Description    :
 Author         :       pingz
 Date           :       2018/4/27
----------------------------------------------
"""

__author__ = 'pingz'


# 带有yield的函数就是生成器
def counter(start_at=0):
    count = start_at
    while True:
        val = (yield count)
        if val is not None:
            count = val
        else:
            count += 1
    # 生成器出现异常时，返回提示信息
    return "Wrong: counter overflow."


"""
在需要迭代穿越一个对象时，优先考虑使用生成器替代迭代器，使用生成器表达式替代列表解析。
"""


if __name__ == "__main__":

    for x in counter(6):
        if x > 10:
            break
        print("call counter(6) = ", x)

    g = (x*2 for x in range(3))    # 生成器的列表生成式，只是得到一个生成器，不会执行生成器里面的语句
    """
    #print(dir(g))       # 内置函数dir()：得到对象的所有可调用方法
    """
    try:
        print(next(g))   # 调用next()，才执行生成器里面的语句
        print(next(g))
        print(next(g))
        print(next(g))
    except StopIteration as e:
        print("call next(g) error: ", e.value)


