
* 直接执行  
比如:  ./xxx.py，在py文件头加入下面两句，注意顶头不要空格  
```python
#!/usr/bin/python
#-*- coding: UTF-8 -*-
```
* pdb 调试   
python -m pdb xxx.py  
设置条件断点  
b 10,var==2

* pyinstaller  
可用 pyinstaller -F xxx.py 生成执行文件，可执行文件位于 dist 目录下。注意，在只安装一个版本的python环境中运行此命令，否则有莫名其妙的错误，例如找不到已安装的模块。
