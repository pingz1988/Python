#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import time
import datetime
import commands

#保留文件数
limit = 100
dir = r'/mvtech/CSMS/ftplocalpath/DataCollect/14/'
dir += datetime.datetime.now().strftime("%Y-%m-%d")
dir += r'/5/'
cmd_fn = ((r"ls -l %s|grep ^- |wc -l") % dir)
#fn = int(commands.getoutput(cmd_fn))
fn = 0
with os.popen(cmd_fn, "r") as p:
    fn = int(p.read())
    print("--- fn: %d" % fn)
cmd = ((r"ls -rt %s | tail -200") % dir)
  
while(1):
    while(fn > limit):
        with os.popen(cmd, "r") as p:
            for filename in p.readlines():
                file_path = dir + filename
                idx = file_path.find(".pcap")
                if (idx == -1):
                    continue
                idx += len(".pcap")
                print("--- Delete File: %s" % filename)
                file_path = file_path[:idx]
                os.remove(file_path)
                fn = fn - 1
                if(fn == limit):
                    break   
    with os.popen(cmd_fn, "r") as p:
        fn = int(p.read())
    time.sleep(1)