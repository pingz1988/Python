```python
#!/usr/bin/python
# coding: utf-8

import os
import time
import datetime

def is_process_running(process_id):
        try:
                os.kill(process_id, 0)
                return True
        except OSError:
                return False

def is_process_alive(process_name):
        with os.popen("pidof " + process_name) as f:
                if len(f.readlines()) > 0:
                        return True
        return False

process_dict = {"eu":"/home/pingz/code/telcom", "fa":"/home/pingz/code/telcom", "xdr":"/home/pingz/code/telcom", "upload":"/home/pingz/code/telcom"}

while(1):
        for process,work_dir in process_dict.items():
                dt = datetime.datetime.now()
                alive = is_process_alive(process)
                if alive:
                        print("%s [%s staus]: %s" % (dt.strftime('%Y-%m-%d %I:%M:%S %p'), process, "enable"))
                else:
                        print("\033[1;31m %s [%s staus]: %s. start it now.\033[0m" % (dt.strftime('%Y-%m-%d %I:%M:%S %p'), process, "disable"))
                        cmd = ("cd %s;./%s &" % (work_dir, process))  # 多条语句用";"或“&&”连接，“&”表示不阻塞
                        #os.system(cmd)
                        os.popen(cmd)  # 不等待运行完成
        time.sleep(1)
```
