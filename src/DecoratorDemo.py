# -*- coding=utf-8 -*-
# !/usr/bin/env python

"""
----------------------------------------------
 File Name      :       decorator_use
 Description    :       装饰器练习
 Author         :       pingz
 Date           :       2018/4/26
----------------------------------------------
"""

__author__ = 'pingz'


# 函数装饰器，装饰func函数。使用了嵌套函数和高阶函数（函数作为返回值）
def func_decorator(func):
    def wrapper(*args, **kwargs):
        print("ready to call func...")
        func(*args, **kwargs)
        print("func done.")

    return wrapper


@func_decorator
def func(n):
    print("Func is called. Arg of func is ", n)


# 类方法装饰器
def class_func_decorator(class_func):
    def wrapper(instance):
        print("Testing class func decorator...")
        class_func(instance)
        print("Test done.")

    return wrapper


class MyTest(object):
    @class_func_decorator
    def class_func(self):
        print("class_func called.")


# 装饰器带参数
def decorator_with_args(decorator_type):
    def outer_wrapper(func):
        if decorator_type == "func_deco":
            def wrapper(*args, **kwargs):
                print("ready to call func...")
                func(*args, **kwargs)
                print("func done.")
            return wrapper
        else:
            print("invalid decorator type")
    return outer_wrapper


@decorator_with_args("func_deco")
def func1():
    print("func1 called.")


# 多装饰器修饰函数
def deco1_func(func):
    def wrapper(*args,**kwargs):
        func(*args,**kwargs)
        print("decorator 1")
    return wrapper


def deco2_func(func):
    def wrapper(*args,**kwargs):
        func(*args,**kwargs)
        print("decorator 2")
    return wrapper

@deco1_func
@deco2_func
def some_deco_test():
    print("some_deco_test called.")


if __name__ == '__main__':
    some_deco_test()        # 多装饰器

    func(10)

    test = MyTest()
    test.class_func()
