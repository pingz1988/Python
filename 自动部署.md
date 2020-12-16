```python
#!/usr/bin/python
# -*- coding: UTF-8 -*-
import getopt
import sys
import paramiko
import threading
from scp import SCPClient
  

'''
********************************************************************
说明：
不带参数运行本脚本时，file_list中的文件都会上传；

参数：
-h/--help:      显示帮助信息
-e/--exec:      执行命令 [cmd]
-s/--send:      发送文件 [file_path]
-v/--version:   显示版本号
********************************************************************
'''
file_list = [
            "send_file/eu.ini", 
            "send_file/assemble_cache.ini", 
            "send_file/upload.ini", 
            "send_file/dpdk-init.sh",
            "send_file/config.sh",
            "send_file/EU_CTCC.tar.gz"
            ]


def get_host_list():
    host_list = []
    with open('host.ini', 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#'):
                continue
            host_list.append(tuple(line.split(',')))
    return host_list


def send_file(host,port,username,password,file_path,remote_path):
    ssh = paramiko.SSHClient()
    try:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh.connect(host,port,username,password)
        scpclient = SCPClient(ssh.get_transport(),socket_timeout=10.0)
        scpclient.put(file_path, remote_path)
        print("%s: %s [ Ok ]" % (host,file_path))
    except Exception as e:
        print("%s: %s %s [ Error ]" % (host,file_path,e))
    ssh.close()


def send_file_to_all(host_list,file_path,remote_path):
    for host,port,username,password in host_list:
        send_file(host,port,username,password,file_path,remote_path)


def send_files(host,port,username,password,remote_path):
    print("%s:\n    send files [ Start ]" % host)
    
    with paramiko.SSHClient() as ssh: 
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        try:
            ssh.connect(host, port, username, password)
            with SCPClient(ssh.get_transport(),socket_timeout=5.0) as scp:
                # 上传 file_list 中指定的文件 
                for file_path in file_list:
                    print("    sending %s ..." % file_path)
                    scp.put(file_path, remote_path)
                    print("    send %s [ Ok ]" % file_path)
                
                # 上传 host 对应的 encode_data 
                encode_data = "encode_data/" + host + '_' + "encode_data"
                print("    sending %s ..." % encode_data)
                scp.put(encode_data, remote_path)
                print("    send %s [ Ok ]" % encode_data)
        except Exception as e:
            print("    %s [ Error ]" % e)
            print("    send files [ End ]\n")
            return False
    
    print("    send files [ End ]\n")
    
    return True


def send_files_to_all(host_list,remote_path):
    for host,port,username,password in host_list:
        send_files(host,port,username,password,remote_path)  


def exec_cmd(host,port,username,password,command):
    print("%s:\n%s" % (host,command))
    
    ssh = paramiko.SSHClient()
    try:
        policy = paramiko.AutoAddPolicy()
        ssh.set_missing_host_key_policy(policy)
        ssh.connect(host,port,username,password)
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read().decode(encoding='UTF-8',errors='strict')
        error = stderr.read().decode(encoding='UTF-8',errors='strict')

        if len(error) != 0:
            print("result: [ Failed ]\n%s" % error)
        else:
            print("result: [ Ok ]\n%s" % result)
    except Exception as e:
        print("result: [ Error ]\n%s" % e)
    ssh.close()


def exec_on_all(host_list,command):
    for ip,port,username,password in host_list:
        exec_cmd(ip,port,username,password,command)


def show_help():
    print("usage:")
    print("    -h: show this help")
    print("    -e: execute command, eg1: -e ls    eg2: -e \"ls -l\"")
    print("    -s: send file_path, eg: -s xxx.ini")
    print("    -v: show version")
    print("    send files without parameters")
 

if __name__ == "__main__":
    print()
    
    host_list = get_host_list()
    if len(host_list) == 0:
        print("err: host list is empty")
        sys.exit()
   
    print("host.ini: %d hosts\n" % len(host_list))
    
    if len(sys.argv) == 1:
        send_files_to_all(host_list,remote_path="/tmp/")
        exec_on_all(host_list,"cd /tmp/ && chmod +x ./config.sh && ./config.sh")
        sys.exit()


    try:
        opts,args = getopt.getopt(sys.argv[1:],'he:s:v',['help','exec=','send=','version'])
        for name,value in opts:
            if name in ('-h','--help'):
                show_help()
                sys.exit()
            elif name in ('-e','--exec'):
                cmd = value
                if len(cmd) == 0:
                    print("-e args err.")
                    show_help()
                    sys.exit()
                exec_on_all(host_list,cmd)
            elif name in ('-s', '--send'):
                file_path = value
                if len(file_path) == 0:
                    print("-s args err.")
                    show_help()
                    sys.exit()
                send_to_all(host_list, file_path)
            elif name in ('-v','--version'):
                print("version: EU_CUC_1.0.0")
                sys.exit()
            else:
                show_help()
                sys.exit()
    except getopt.GetoptError:
        print("invalid args.")
        show_help()
        sys.exit()
 ```
