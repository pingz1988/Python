# -*- coding=utf-8 -*-
# !/usr/bin/env python

import math
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from pylab import *

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

if __name__ == '__main__':
    file = open('link.txt', 'r')
    linesList = file.readlines()
    linesList = [line.strip().split(' ') for line in linesList]
    file.close()
    lon = [round(float(x[0]), 6) for x in linesList]
    print(lon)
    lat = [round(float(x[1]), 6) for x in linesList]
    print(lat)

    plt.figure()
    plt.plot(lon, lat, 'bo')
    plt.plot(lon, lat, '--r')
    plt.xlabel(u'经度')
    plt.ylabel(u'纬度')
#    plt.xlim(30.0, 31.0)
#    plt.ylim(114.0, 115.0)
    plt.title(u'轨迹拟合')
    plt.grid(True, linestyle="-.")
    plt.legend()
    plt.show()
