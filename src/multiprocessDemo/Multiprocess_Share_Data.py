# modified from official documentation

# -*- coding=utf-8 -*-
# !/usr/bin/env python

import multiprocessing
import queue


def f(n, a):
    n.value = 3.14
    # 普通类型判断用type，类对象的类型判断用isinstance方法
    if type(a) == type(multiprocessing.Array("i", range(10))) and len(a) > 0:
        a[0] = 5


def modify(q):
    if type(q) == type(multiprocessing.Queue()):
        q.put(100)


if __name__ == '__main__':
    # 1、使用Value/Array结构进行数据共享
    num = multiprocessing.Value('d', 0.0)   # 双精度数(d), 并初始化为0.0
    arr = multiprocessing.Array('i', range(10)) # 整数

    p = multiprocessing.Process(target=f, args=(num, arr))
    p.start()
    p.join()

    print(num.value)
    print(arr[:])

    # 2、Queue
    q = multiprocessing.Queue(maxsize=10)
    q.put(123)
    p = multiprocessing.Process(target=modify, args=(q,))
    p.start()
    p.join()
    while not q.empty():
        print("element: ", q.get())

    q = queue.PriorityQueue(maxsize=10)
    q.put(2,20)
    q.put(1,10)
    q.put(0,100)
    while not q.empty():
        print("element in PriorityQueue: ", q.get())

