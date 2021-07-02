#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import configparser
from ftplib import FTP
import time


'''
def get_fn_cmd(dir):
    cmd_fn = ((r"ls -l %s|grep ^- |wc -l") % dir)
    return cmd_fn

    
def get_upload_cmd(dir):
    cmd = ((r"ls -rt %s | tail -1000") % dir)
    return cmd
'''

def find_dst_file(dir, suffix_list):
    for root, ds, fs in os.walk(dir):
        for f in fs:
            suffix = f.split(".")[1]
            if suffix in suffix_list:  # 只要目标后缀的文件名
                fullname = os.path.join(root, f)
                yield fullname
        

def upload(ftp, fpath, remote_path):
    try:
        with open(fpath, "rb") as fp:
            buf_size = 10240
            try:
                ftp.storbinary("STOR {}".format(remote_path), fp, buf_size)
                print("Uploaded: %s -> %s" % (fpath, remote_path))
                return True
            except Exception as e:
                print("--- Upload failed: %s -> %s    reason: %s" % (fpath, remote_path, e))
                return False
    except Exception as e:
        print("--- Upload failed: %s -> %s    reason: %s" % (fpath, remote_path, e))
        return False

def upload_dir(ftp, dir, suffix_list, bak_dir, remote_dir):
    for fpath in find_dst_file(dir, suffix_list):
        fname = os.path.basename(fpath)
        remote_path = remote_dir + fname
        if (upload(ftp, fpath, remote_path)):
            try:
                os.remove(fpath)
                print("Removed: %s" % (fpath))
            except:
                print("--- Remove failed: %s" % (fpath))
                pass
            '''
            bak_path = bak_dir + fname
            try:
                os.rename(fpath, bak_path)
                print("Moved: %s -> %s" % (fpath, bak_path))
            except Exception as e:
                print("--- Move failed: %s -> %s    reason: %s" % (fpath, bak_path, e))
            '''
            

'''
def download(f, remote_path, local_path):
    fp = open(local_path, "wb")
    buf_size = 1024
    f.retrbinary('RETR {}'.format(remote_path), fp.write, buf_size)
    fp.close()
'''


if __name__ == "__main__":
    config = configparser.ConfigParser()
    path = r'conf.ini'
    config.read(path)
    host = config['ftp']['host']
    port = config['ftp']['port']
    username = config['ftp']['username']
    password = config['ftp']['password']
    dir = config['ftp']['local_dir']
    suffixs = config['ftp']['suffix_set']
    suffix_list = suffixs.split(',')
    bak_dir = config['ftp']['local_bak_dir']
    remote_dir = config['ftp']['remote_dir']
    
    print("host: %s, port: %s, username: %s, password: %s" % (host, port, username, password))
    
    ftp = FTP()
    ftp.connect(host, int(port), 30)
    ftp.login(username, password)
    ftp.set_debuglevel(0)
    
    '''
    while(1):
        cmd_fn = get_fn_cmd(dir)
        with os.popen(cmd_fn, "r") as p:
            fn = int(p.read())
            while(fn > 0):
                cmd = get_upload_cmd(dir)
                with os.popen(cmd, "r") as pp:
                    for filename in pp.readlines():
                        file_path = dir + filename
                        idx = file_path.find(".zip")
                        if (idx == -1):
                            continue
                        idx += len(".zip")
                        print("--- Delete File: %s" % filename)
                        file_path = file_path[:idx]
                        try:
                            os.remove(file_path)
                        except:
                            pass
    '''
    
    while(1):
        upload_dir(ftp, dir, suffix_list, bak_dir, remote_dir)
        time.sleep(1)
    
    ftp.quit()
