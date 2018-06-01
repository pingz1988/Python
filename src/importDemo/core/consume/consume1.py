# -*- coding=utf-8 -*-
# !/usr/bin/env python

"""
----------------------------------------------
 File Name      :       consume
 Description    :
 Author         :       pingz
 Date           :       2018/4/28
----------------------------------------------
"""

__author__ = 'pingz'

import consume2


class Cls1(object):
    data = "I'm public variate."       # public variate

    def __init__(self):
        print("Cls1 init.")

    @classmethod
    def test(cls):
        print("classmethod test() called.")

    def __myTest(self):
        print("this is private method")


def consume1_func():
    print("Consume1 function.")


if __name__ == "__main__":
    print("in consume 1 main.")

