```python

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, os
import sys

try:
    import pexpect
except ImportError:
    os.system('yum install pexpect -y')
    time.sleep(3)
    check_pexpect = os.popen('rpm -qa | grep pexpect')
    if 'pexpect' in check_pexpect.read():
        import pexpect
    else:
        print 'can not find pexpect module, exit now.'
        sys.exit()


def scp_file(local_path, ssh_user, ssh_ip, ssh_path, ssh_pwd):
    try:
        scp_cmd = pexpect.spawn('scp ' + local_path + ' ' + ssh_user + '@' + ssh_ip + ':' + ssh_path)
        expect_result = scp_cmd.expect([r'password:', r'yes/no'], timeout=30)
        if expect_result == 0:
            scp_cmd.sendline(ssh_pwd)
            scp_cmd.read()  # don't delete this code,if your do then,the program will be faill.
        elif expect_result == 1:
            scp_cmd.sendline('yes')
            scp_cmd.expect('password:', timeout=30)
            scp_cmd.sendline(ssh_pwd)
            scp_cmd.read()  # don't delete this code,if your do then,the program will be faill.
    except pexpect.EOF:
        print 'scp ' + local_path + ' fail'
        print pexpect.EOF
    except pexpect.TIMEOUR:
        print 'scp ' + local_path + ' timeout'
        time.sleep(2)

if '__name__' == '__main__':
    local_path = r'/home/zhangping/scp_test.txt'
    ssh_user = r'root'
    ssh_ip = r'192.168.1.245'
    ssh_path = r'/home/pingz/'
    ssh_pwd = r'mvtech@123!'
    scp_file(local_path, ssh_user, ssh_ip, ssh_path, ssh_pwd)
    
 ```
