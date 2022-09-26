```python

#!/usr/bin/python3
# -*- coding=utf-8 -*-
#python version 3.7
import os
import sys
import glob
import time
import pytest


'''
说明：
    1、此脚本适用于《移动互联网恶意软件监控系统接口规范v2.0-20220902_V1-修订版.docx》5.2.4章节描述的日志
    2、运行方式：python3 -m pytest
'''

'''
fixture 装饰器，是作为一个参数，传给 test_ 开头的测试函数使用的；
其中，scope的取值:
    module 表示当前py文件只调用一次; 
    session 表示多个py文件调用一次，可以跨py文件调用
'''
@pytest.fixture(scope="module")
def proto_name_list():
    l = []
    fpath = 'attach_9_proto_name.txt'  #取自附录9 应用层协议
    with open(fpath) as f:
        for line in f:
            l.append(line.strip())
    return l


class TestEvtLog():
    head_field_cnt = 7
    head_must_option_indexes = [1,2,3,4,5,7]
    must_option_indexes = [1,2,3,4,5,6,7,8,9,10,11,19,20,22,23,25,28,29,31,32,33,34,35,36,37,38,39,40,41,44]
    field_cnt = 57
    log_type = 'EVT'
    fname_delimiter = '_'
    pattern = f'{log_type}{fname_delimiter}*.txt'  #支持绝对路径
    fname_split_cnt = 4
    log_delimiter = '|'
    
    def check_path(self, fpath):
        l = fpath.split(self.fname_delimiter)
        assert self.fname_split_cnt == len(l), f'文件名{fpath}不符合格式'
        
    def check_field_cnt(self, l, is_head):
        if is_head:
            assert len(l) == self.head_field_cnt, f'{self.log_type}日志-首行字段数不正确'
        else:
            assert len(l) == self.field_cnt, f'{self.log_type}日志-正文字段数不正确'
        
    def check_must_option(self, l, must_option_indexes):
        for i in must_option_indexes:
            assert len(l[i-1]) > 0, f'{self.log_type}日志-正文第{i}个字段为必填项，但未填'
        
    def check_head(self, head):
        l = head.split(self.log_delimiter)
        self.check_field_cnt(l, True)
        self.check_must_option(l, self.head_must_option_indexes)
            
    def check_time(self, i, strtime, fmt):
        # 参数 i: 表示字段索引，从 1 开始
        is_ok = False
        try:
            time.strptime(strtime, fmt)  #检查 {strtime} 是否符合 {fmt} 指定的格式
            is_ok = True
        except:
            is_ok = False
        assert is_ok, f'{self.log_type}日志-第{i}个字段{strtime}时间格式不符合要求'
        
    def check_int_range(self, i, s, imin, imax):
        v = imin - 1
        try:
            v = int(s)
        except:
            pass
        assert imin <= v <= imax, f'{self.log_type}日志-第{i}个字段{s}不在值域内'
        
    def check_int_list(self, i, s, l):
        is_ok = False
        try:
            v = int(s)
            if v in l:
                is_ok = True
        except:
            pass
        assert is_ok, f'{self.log_type}日志-第{i}个字段{s}不在值域内'
        
    def check_int(self, i, s):
        is_ok = False
        try:
            v = int(s)
            is_ok = True
        except:
            pass
        assert is_ok, f'{self.log_type}日志-第{i}个字段{s}类型不是int'
        
    def check_proto_name(self, i, proto_name, proto_name_list):
        assert proto_name in proto_name_list, f'{self.log_type}日志-第{i}个字段{proto_name}应用层协议名称不在规范内'
            
    def check_body(self, f, proto_name_list):
        for line in f:
            line = line.strip()
            l = line.split(self.log_delimiter)
            
            self.check_field_cnt(l, False)
            self.check_must_option(l, self.must_option_indexes)
            
            i = 19  # 第19个字段
            self.check_time(i, l[i-1], "%Y-%m-%d %H:%M:%S")
            
            i = 23  # 第23个字段
            self.check_int_range(i, l[i-1], 0, 8)
            
            i = 28
            self.check_int_range(i, l[i-1], 0, 3)
            
            i = 29
            self.check_int_range(i, l[i-1], 0, 3)
            
            i = 31
            v = [6,17]
            self.check_int_list(i, l[i-1], v)
            
            i = 32
            self.check_proto_name(i, l[i-1], proto_name_list)
            
            i = 33
            v = [0,1]
            self.check_int_list(i, l[i-1], v)
            
            i = 35
            self.check_int_range(i, l[i-1], 0, 65535)
            
            i = 37
            self.check_int_range(i, l[i-1], 0, 65535)
            
            for i in [38,39,40,41]:
                self.check_int(i, l[i-1])
                
            i = 44
            v = [0,1]
            self.check_int_list(i, l[i-1], v)
        
    def test_log(self, proto_name_list):
        fpaths = glob.iglob(self.pattern)
        for fpath in fpaths:
            self.check_path(fpath)
            with open(fpath, 'r') as f:
                self.check_head(next(f))
                self.check_body(f, proto_name_list)

            
class TestDesLog():
    must_option_indexes = [1,2,3,4,5,6,7,8,9,10,11]
    head_field_cnt = 7
    head_must_option_indexes = [1,2,3,4,5,7]
    field_cnt = 48
    log_type = 'DES'
    fname_delimiter = '_'
    pattern = f'{log_type}{fname_delimiter}*.txt'  #支持绝对路径
    log_delimiter = '|'
        
    def check_path(self, fpath):
        l = fpath.split(self.fname_delimiter)
        assert self.fname_split_cnt == len(l), f'文件名{fpath}不符合格式'
        
    def check_head(self, head):
        l = head.split(self.log_delimiter)
        assert len(l) == self.head_field_cnt, f'{self.log_type}日志-首行信息字段数不正确'
        for i in self.head_must_option_indexes:
            assert len(l[i-1]) > 0, f'{self.log_type}日志-首行第{i}个字段为必填项，但未填'
            
    def check_body(self, f):
        for line in f:
            l = line.split(self.log_delimiter)
            
            self.check_field_cnt(l, self.field_cnt)
            self.check_must_option(l, self.must_option_indexes)
            
            f19_ok = False
            try:
                time.strptime(l[18], "%Y-%m-%d %H:%M:%S")  #检查第19个字段: 事件时间，格式为YYYY-MM-DD HH:MM:SS
                f19_ok = True
            except:
                f19_ok = False
            assert f19_ok, f'{self.log_type}日志-第19个字段{l[18]}时间格式不正确'
        
    def test_log(self):
        fpaths = glob.iglob(self.pattern)
        for fpath in fpaths:
            self.check_path(fpath)
            with open(fpath, 'r') as f:
                self.check_head(next(f))
                self.check_body(f)

            
class TestPrcLog():
    head_field_cnt = 7
    head_must_option_indexes = [1,2,3,4,5,7]
    must_option_indexes = [1,2,3,4,5,6,7,8,9,10,11,19,20,22,23,25,28,29,31,32,33,34,35,36,37,38,39,40,41,44]
    field_cnt = 57
    log_type = 'PRC'
    fname_delimiter = '_'
    pattern = f'{log_type}{fname_delimiter}*.txt'  #支持绝对路径
    fname_split_cnt = 4
    log_delimiter = '|'
    
    def check_path(self, fpath):
        l = fpath.split(self.fname_delimiter)
        assert self.fname_split_cnt == len(l), f'文件名{fpath}不符合格式'
        
    def check_field_cnt(self, l, is_head):
        if is_head:
            assert len(l) == self.head_field_cnt, f'{self.log_type}日志-首行字段数不正确'
        else:
            assert len(l) == self.field_cnt, f'{self.log_type}日志-正文字段数不正确'
        
    def check_must_option(self, l, must_option_indexes):
        for i in must_option_indexes:
            assert len(l[i-1]) > 0, f'{self.log_type}日志-正文第{i}个字段为必填项，但未填'
        
    def check_head(self, head):
        l = head.split(self.log_delimiter)
        self.check_field_cnt(l, True)
        self.check_must_option(l, self.head_must_option_indexes)
            
    def check_time(self, i, strtime, fmt):
        # 参数 i: 表示字段索引，从 1 开始
        is_ok = False
        try:
            time.strptime(strtime, fmt)  #检查 {strtime} 是否符合 {fmt} 指定的格式
            is_ok = True
        except:
            is_ok = False
        assert is_ok, f'{self.log_type}日志-第{i}个字段{strtime}时间格式不符合要求'
        
    def check_int_range(self, i, s, imin, imax):
        v = imin - 1
        try:
            v = int(s)
        except:
            pass
        assert imin <= v <= imax, f'{self.log_type}日志-第{i}个字段{s}不在值域内'
        
    def check_int_list(self, i, s, l):
        is_ok = False
        try:
            v = int(s)
            if v in l:
                is_ok = True
        except:
            pass
        assert is_ok, f'{self.log_type}日志-第{i}个字段{s}不在值域内'
        
    def check_int(self, i, s):
        is_ok = False
        try:
            v = int(s)
            is_ok = True
        except:
            pass
        assert is_ok, f'{self.log_type}日志-第{i}个字段{s}类型不是int'
        
    def check_proto_name(self, i, proto_name, proto_name_list):
        assert proto_name in proto_name_list, f'{self.log_type}日志-第{i}个字段{proto_name}应用层协议名称不在规范内'
            
    def check_body(self, f, proto_name_list):
        for line in f:
            line = line.strip()
            l = line.split(self.log_delimiter)
            
            self.check_field_cnt(l, False)
            self.check_must_option(l, self.must_option_indexes)
            
            i = 19  # 第19个字段
            self.check_time(i, l[i-1], "%Y-%m-%d %H:%M:%S")
            
            i = 23  # 第23个字段
            self.check_int_range(i, l[i-1], 0, 8)
            
            i = 28
            self.check_int_range(i, l[i-1], 0, 3)
            
            i = 29
            self.check_int_range(i, l[i-1], 0, 3)
            
            i = 31
            v = [6,17]
            self.check_int_list(i, l[i-1], v)
            
            i = 32
            self.check_proto_name(i, l[i-1], proto_name_list)
            
            i = 33
            v = [0,1]
            self.check_int_list(i, l[i-1], v)
            
            i = 35
            self.check_int_range(i, l[i-1], 0, 65535)
            
            i = 37
            self.check_int_range(i, l[i-1], 0, 65535)
            
            for i in [38,39,40,41]:
                self.check_int(i, l[i-1])
                
            i = 44
            v = [0,1]
            self.check_int_list(i, l[i-1], v)
        
    def test_log(self, proto_name_list):
        fpaths = glob.iglob(self.pattern)
        for fpath in fpaths:
            self.check_path(fpath)
            with open(fpath, 'r') as f:
                self.check_head(next(f))
                self.check_body(f, proto_name_list)
                

if __name__ == "__main__":
    wd = os.path.abspath(os.path.dirname(sys.argv[0]))
    os.chdir(wd)
    
    pytest.main()

```
