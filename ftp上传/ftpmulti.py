#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import configparser
from ftplib import FTP
import time
from multiprocessing import Pool


def get_fn_cmd(dir):
    cmd_fn = ((r"ls -l %s|grep ^- |wc -l") % dir)
    return cmd_fn


def get_files_cmd(dir):
    cmd = ((r"ls -rt %s | tail -800") % dir)
    return cmd


def upload(arg):
    ftp = arg[0]
    file_list = arg[1]
    remote_dir = arg[2]

    ftp.cwd(remote_dir)

    for localfile in file_list:
        try:
            fname = os.path.basename(localfile)
            remote_path = remote_dir + fname
            with open(localfile, "rb") as fp:
                buf_size = 1024*1024
                ftp.storbinary("STOR %s" % fname, fp, buf_size)
                print("Uploaded: %s -> %s" % (localfile, remote_path))
        except Exception as e:
            print("--- Upload failed: %s -> %s    reason: %s" % (localfile, remote_path, e))
            continue

    ftp.quit()


def get_files_list(dir, suffix_list, n):
    cmd = get_files_cmd(dir)
    files_list = [[] for i in range(n)]
    with os.popen(cmd, "r") as pp:
        i = 0
        for filename in pp.readlines():
            filename = filename.replace("\n","")
            suffix = os.path.splitext(filename)[1]
            if suffix in suffix_list:  # 只取目标后缀的文件
                file_path = dir + filename
                files_list[i%n].append(file_path)
            i = i + 1
    return files_list


def new_ftp(host, port, username, password):
    ftp = FTP()
    ftp.connect(host, int(port), 30)
    ftp.login(username, password)
    return ftp


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
    
    #print("host: %s, port: %s, username: %s, password: %s" % (host, port, username, password))

    while(1):
        N = len(os.sched_getaffinity(0))  # 可用cpu个数
        files_list = get_files_list(dir, suffix_list, N)
        
        print("Processes = %d" % N)

        # 由 N 个进程处理 files_list 中的文件
        pool = Pool(processes=N)
        for i in range(N):
            ftp = new_ftp(host, port, username, password)  # 每个核对应一个进程，每个进程一个ftp连接
            ftp.set_debuglevel(0)
            upload_arg = (ftp, files_list[i], remote_dir)
            pool.apply_async(upload, (upload_arg,))  # 每个进程采用异步上传的方式，并在 upload 中释放 ftp 连接
        pool.close()
        pool.join()
