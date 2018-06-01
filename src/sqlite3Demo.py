#!/usr/bin/env python
# -*- coding: <encoding name> -*-

"""
注意工程目录下的文件名，不要与导入模块名相同
"""
import sqlite3

# 连接数据库
conn = sqlite3.connect('test.db')
print("Opened database successfully")

# 获取游标，执行SQL语句
c = conn.cursor()
# 不存在表才会创建
c.execute('''CREATE TABLE IF NOT EXISTS COMPANY
       (ID INT PRIMARY KEY     NOT NULL,
       NAME           TEXT    NOT NULL,
       AGE            INT     NOT NULL,
       ADDRESS        CHAR(50),
       SALARY         REAL);''')
print("Table created successfully")

# 插入记录，此处使用 INSERT OR REPLACE INTO 表示主键重复时，更新对应记录
c.execute("INSERT OR REPLACE INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
      VALUES (1, 'Paul', 32, 'California', 20000.00 )");
c.execute("INSERT OR REPLACE INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
      VALUES (2, 'Allen', 25, 'Texas', 15000.00 )");
c.execute("INSERT OR REPLACE INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
      VALUES (3, 'Teddy', 23, 'Norway', 20000.00 )");
c.execute("INSERT OR REPLACE INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
      VALUES (4, 'Mark', 25, 'Rich-Mond ', 65000.00 )");
print("Records inserted successfully\n")

conn.commit()       # 写入更新操作时，需要调用commit()方法，否则不会更新到数据库

cursor = c.execute("SELECT id, name, address, salary from COMPANY")
for row in cursor:
   print("ID = ", row[0])
   print("NAME = ", row[1])
   print("ADDRESS = ", row[2])
   print("SALARY = ", row[3], "\n")
print("Operation done successfully")

c.close()
cursor.close()
conn.close()        # close()方法不会自动调用commit()方法
