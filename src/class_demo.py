#!/usr/bin/env python
# -*- coding: <encoding name> -*-

import types

class BaseClass:
    #类实例初始化方法
    def __init__(self, var1=0, var2=0):
        self.m_var1 = var1
        self.m_var2 = var2
        print("call BaseClass")

    def func(self, str):
        if types(str) == types("abc"):
            print(str.upper())
            self.m_var1 = str
            print(self.m_var1)

    @classmethod
    def ClassFunc(cls, parm):
        pass

    @staticmethod
    def StaticFunc():
        pass
