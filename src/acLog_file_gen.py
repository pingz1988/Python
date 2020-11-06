#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import textwrap
import sys
import getopt
import time
import datetime
import random
import base64
import gzip
import shutil

#访问日志手动补数据python脚本#
############################需要手动改部分#####################################
LINE_COUNT = 5000                #需要补的访问日志数据条数
SrcIp = "58.19.58.7"             #访问日志源IP
DestIp = "58.218.194.20"         #访问日志目的IP
PORT_MIN = 8000                  #访问日志源端口起始范围
PORT_MAX = 20000                 #访问日志源端口截止范围
DestPort = 80                    #访问日志目的端口，不变
BussinessType = 204              #业务类型
UpFlows = 2316                   #上行流量
DownFlows = 3561                 #下行流量

#访问日志URL
URL = "http://emo.xz.gov.cn/yjb/zcfg/20170216/021_c7b27b68-07e5-4546-82ed-0d8b671a01ce.htm"

#访问日志起始时间
TIME_START_STR = "2020-09-27 12:00:00.123"
TIME_END_STR   = "2020-09-27 12:30:00.456"

#整个访问日志话单的持续时间，单位为秒
#用来随机计算每条话单的时间，拨测条数越多，持续时间越长，根据经验调整
TIME_DURATION = 120

#访问日志名称                  
FILE_NAME = "202009270000030098591021.txt"

#访问日志拷贝路径（需与程序配置存放访问日志路径一致）
COPY_PATH = "/mvtech/CSMS/ftplocalpath/du_accesslog"
###########################手动修改部分结束####################################

# 修改上述配置后，
# 第一步执行 "./acLog_file_gen.py" 进行补日志操作
# 第二步执行 "./acLog_file_gen.py put" 将补的日志拷贝至访问日志上传目录

########################以下代码不用手动修改####################################
ORIGIN_LINE = "%s|%d|%s|%d|1|%d|%s|9|%d|%d|%s"

def parse_time_ms(time_str):
    obj = datetime.datetime.strptime(time_str,"%Y-%m-%d %H:%M:%S.%f")
    return int(time.mktime(obj.timetuple())*1000.0 + obj.microsecond/1000.0)


TIME_START = parse_time_ms(TIME_START_STR)
TIME_END = parse_time_ms(TIME_END_STR)
t = TIME_START
new_port = PORT_MIN
    
def parse_port(port_range):
    global PORT_MIN
    global PORT_MAX
    global new_port
    values = port_range.split(":")
    assert len(values) >= 2
    PORT_MIN = int(values[0])
    PORT_MAX = int(values[1])
    assert PORT_MAX >= PORT_MIN
    new_port = PORT_MIN

    
def get_next_time(line_no):
    global t
    T = int((TIME_END-TIME_START)/LINE_COUNT)
    if (T < 1):
        T = 1
    t = long(t) + long(T*random.random()*1.5)
    t_head = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(t/1000))
    t_ms = t % 1000
    time_stamp = "%s.%03d" % (t_head, t_ms)
    return time_stamp

    
def get_next_port(line_no):
    global new_port
    new_port = new_port + 1 + 3 * random.random()
    return new_port
    
def write_line(new_file, line_no):
    line = ORIGIN_LINE % (SrcIp, get_next_port(line_no), DestIp, DestPort, BussinessType, get_next_time(line_no), UpFlows, DownFlows, base64.b64encode(URL))
    new_file.write(line)

def main(action):
    if(action == 'creat'):
        with gzip.open("%s.gz" % FILE_NAME, "wb") as new_file: 
            line_no = 1
            while(line_no <= LINE_COUNT):
                write_line(new_file, line_no)
                if line_no != LINE_COUNT:
                    new_file.write('\n')
                line_no += 1
        print("creat %s.gz complete." % FILE_NAME)
    elif(action == 'put'):
        CUR_FILE = "%s.gz" % FILE_NAME
        NEW_FILE = "%s/%s.gz" % (COPY_PATH, FILE_NAME)
        shutil.copyfile(CUR_FILE, NEW_FILE)
        print("copy file: %s -> %s" % (CUR_FILE, NEW_FILE))
    else:
        show_usage()


def show_usage():
    print("Usage:\n\
                    step 1: ./acLog_file_gen.py         # create log\n\
                    step 2: ./acLog_file_gen.py put     # copy log to %s\n" % COPY_PATH)


if __name__ == "__main__":
    PARA_NUM = len(sys.argv)
    if PARA_NUM == 1:
        action = "creat"
        main(action)
        print("check created log and enter './acLog_file_gen.py put' to upload.")
    elif PARA_NUM == 2:
        action = sys.argv[1]
        main(action)
    else:
        show_usage()

