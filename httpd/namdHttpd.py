```python

#!/usr/bin/python3
# -*- coding=utf-8 -*-
#python version 3.7
import os
import sys
import time
import hashlib
import requests
import psutil
import configparser
#
import codecs
import xml.dom.minidom
import xml.etree.ElementTree as ET
#for https server
from http.server import HTTPServer, BaseHTTPRequestHandler  
import socket  
import ssl
#for sftp
import paramiko
#for http client
from urllib import request
#
import json
# keyfile, cert_file 已弃用，需使用 ssl.SSLContext.load_cert_chain()，使用 try-except 捕获异常
import logging
from logging import handlers
#
from multiprocessing import Process
import threading
#
import shutil
import base64
from enum import Enum

class GlobalConf:
    def __init__(self):
        self.cpu = 0
        self.port = 8199
        self.token = ''
        self.download_to_dir = ''
        self.dev_id = ''
        self.dev_type = 8
        self.vendor_id = ''
        self.upgrade_report_host = '9.9.9.8'
        self.upgrade_report_port = 9998
        self.status_report_host = '9.9.9.9'
        self.status_report_port = 9999
        self.version = 'V1.0'
        self.dev_status_dir = './devStatus'
        
    def check(self):
        err_set = set()
        err_set.add(0 == self.cpu)
        err_set.add(os.cpu_count() <= self.cpu)
        err_set.add(0 == self.port)
        err_set.add(0 == len(self.token))
        err_set.add(0 == len(self.download_to_dir))
        err_set.add(0 == len(self.dev_id))
        err_set.add(not self.dev_type in [5,6,7,8])
        err_set.add(0 == len(self.vendor_id))
        err_set.add(0 == len(self.upgrade_report_host))
        err_set.add(0 == self.upgrade_report_port)
        err_set.add(0 == len(self.status_report_host))
        err_set.add(0 == self.status_report_port)
        err_set.add(0 == len(self.version))
        err_set.add(0 == len(self.dev_status_dir))
        if any(err_set):
            return False
        if not os.path.exists(self.download_to_dir):
            os.makedirs(self.download_to_dir, 777)
        if not os.path.exists(self.dev_status_dir):
            os.makedirs(self.dev_status_dir, 777)
        return True
        
    def parse(self, fpath):
        config = configparser.ConfigParser()
        try:
            if len(config.read(fpath)):
                # [Interact]
                section = 'Interact'
                self.cpu = int(config.get(section, "bind_cpu"))
                self.port = int(config.get(section, "port"))
                self.token = config.get(section, "token")
                self.download_to_dir = config.get(section, "to_local_dir")
                self.upgrade_report_host = config.get(section, "upgrade_report_host")
                self.upgrade_report_port = config.get(section, "upgrade_report_port")
                self.status_report_host = config.get(section, "status_report_host")
                self.status_report_port = int(config.get(section, "status_report_port"))
                # [Device]
                section = 'Device'
                self.dev_id = config.get(section, "dev_id")
                self.dev_type = int(config.get(section, "dev_type"))
                self.vendor_id = config.get(section, "vendor_id")
                self.version = config.get(section, "version")
                
                return self.check()
            else:
                logging.error('read fail: %s', fpath)
                return False
        except Exception as e:
            logging.error('parse %s fail: %s', fpath, e)
            return False  


def untargz(targz, dst_dir):
    t = tarfile.open(targz)
    t.extractall(path=dst_dir)
    return t.getnames()


class RunningCfgPlc:
    def __init__(self):
        self.stfreq = 300  # 状态上报报文的频度，单位为秒，默认5分钟
        self.ntpsvr_ver = ''
        self.ntpsvr_ip = '1.1.1.1'
        self.ntpsvr_interval = 1  # 建议分析/处置模块执行时间同步的间隔，单位分钟
        
    def parse(self, targz, dir):
        names = untargz(targz, dir)
        xml_path = ''
        if len(names):
            xml_path = os.path.join(dir, names[0])
        else:
            logging.error('untargz fail: %s', targz)
        if not os.path.exists(xml_path):
            logging.error('xml not exists: %s', xml_path)
            return False
        tree = ET.parse(xml_path)
        root = tree.getroot()
        self.stfreq = int(tree.find('stfreq').text)
        elem = tree.find('ntpsvr')
        self.ntpsvr_ver = elem.attrib['ver']
        self.ntpsvr_ip = elem.attrib['ip']
        self.ntpsvr_interval = int(elem.attrib['interval'])
        
    
# http/https    
class HttpOps:
    #通讯令牌定义为：token令牌+时间戳（yyyymmddhhmmss）进行md5，MD5值大写（填写方式为2218A25377CF87A5C9DB6DCE7C64060F20210829112320，在基于此格式计算token令牌加时间戳的MD5值）,再将md5值+时间戳（填写方式为md5:时间戳）进行base64编码后的取值。
    @staticmethod
    def make_auth_token(token):
        timestamp = time.strftime("%Y%m%d%H%M%S")
        auth_token = f'{token}{timestamp}'
        auth_token = hashlib.md5(auth_token.encode(encoding='utf-8')).hexdigest().upper()
        auth_token = f'{auth_token}:{timestamp}'
        auth_token = base64.b64encode(auth_token.encode("utf-8"))
        return auth_token.decode()
        
    @staticmethod
    def send_http_basic_auth(url, auth_token):  
        header = f'Authorization: Basic {auth_token}'
        result = requests.post(url, headers=header)
        if result.status_code == 200:
            logging.info('Authorization ok')
            return True
        else:
            logging.error('Authorization fail: %d' % int(result.status_code))
            return False

    def parse_https_auth(header):
        auth = ""
        return auth
            
    @staticmethod
    def check_auth(auth):
        try:
            str = base64.b64decode(auth).decode("utf-8")
            l = str.split(':')
            if 2 != len(l):
                logging.error('check_auth fail: auth=%s', str)
                return (500, 'server err')
            md5 = l[0].upper()
            timestamp = l[1]
            auth_token = f'{g_cfg.token}{timestamp}'
            local_md5 = hashlib.md5(auth_token.encode(encoding='utf-8')).hexdigest().upper()
            if local_md5 == md5 and int(time.time() - int(timestamp)) <= 1800:  #30分钟
                return (200, '')
            if local_md5 != md5:
                logging.error('check_auth fail: local md5=%s md5=%s', local_md5, md5)
                return (401, r'token认证信息有误')
            if int(time.time() - int(timestamp)) > 1800:
                logging.error('check_auth fail: timeout')
                return (401, r'认证时间超过系统要求的安全认证时间')
        except Exception as e:
            logging.error('check_auth %s fail: %s', auth, e)
            return (500, 'server err')
        
    @staticmethod
    def http_post_file(url, headers, fpath):
        result = requests.post(url, headers=headers, files=fpath)
        if result.status_code == 200:
            logging.info('http post %s => %s ok', fpath, url)
            return True
        else:
            logging.error('http post %s => %s fail: %d' , fpath, url, int(result.status_code))
            return False
        
    @staticmethod
    def get(url, json):
        resp = requests.get(url, json)
        return resp.content
        
    @staticmethod
    def https_post_file(url, headers, fpath):
        try:
            with open(fpath,'rb') as fp:
                body = fp.read()
                result = requests.post(url, headers=headers, data=body, verify=False)
                if result.status_code == 200:
                    logging.info('https post %s=>%s ok', fpath, url)
                    return True
                else:
                    logging.error('https post %s=>%s fail. Status code: [%d]', fpath, url, int(result.status_code))
                    return False
        except Exception as e:
            logging.error('https post %s=>%s fail: %s', fpath, url, e)
            return False
        

class UpgradeCmdAttr:
    def __init__(self):
        self.sid = ""
        self.type = 0
        self.timestamp = 0
        
    def check(self):
        if 0 == len(self.sid) or 0 == self.type or 0 == self.timestamp:
            logging.error('check cmdattr fail: incomplete attr')
            return False
        if not self.type in [5,6,7,8]:
            logging.error('check cmdattr fail: invalid type')
            return False
        return True


class EnumUpgradeCode(Enum):
	E_OK = 0
	E_INIT_FAIL = 1
	E_NOT_SUPPORT = 2
	E_PATH_ERR = 3
	E_DOWNLOAD_FAIL = 4
	E_FMT_ERR = 5
	E_COMBIN_FAIL = 6
	E_NOTIFY_FAIL = 7


class UpgradeCmdDb:
    upgrade_result_dict = {
                    EnumUpgradeCode.E_OK.value:'rule update success', 
                    EnumUpgradeCode.E_INIT_FAIL.value:'db init fail',
                    EnumUpgradeCode.E_NOT_SUPPORT.value:'db not support',
                    EnumUpgradeCode.E_PATH_ERR.value:'db update path error',
                    EnumUpgradeCode.E_DOWNLOAD_FAIL.value:'db download fail',
                    EnumUpgradeCode.E_FMT_ERR.value:'db format error',
                    EnumUpgradeCode.E_COMBIN_FAIL.value:'db combine fail',
                    EnumUpgradeCode.E_NOTIFY_FAIL.value:'db notify fail'}

    def __init__(self):
        self.id = ''
        self.version = ''
        self.path = ''  # sftp路径：sftp://用户名:密码@host:port/xxxx/110101FC024_20220830171346.txt.gz
        self.md5 = ''
        self.num = 0
        #
        self.local_path = ''
        self.upgrade_code = -1
        
    
    def check(self):
        err_set = set()
        err_set.add(0 == len(self.id))
        err_set.add(0 == len(self.version))
        err_set.add(0 == len(self.path))
        err_set.add(0 == len(self.md5))
        #err_set.add(0 == self.num)
        if any(err_set):
            return False
        return True
        
    def check_md5(self, md5):
        m1 = self.md5.upper()
        m2 = md5.upper()
        if m1 == m2:
            return True
        return False


#例如：sftp://用户名:密码@host:port/xxxx/110101FC024_20220830171346.txt.gz
def parse_sftp_info(sftp_path):
    user = ''
    passwd = ''
    host = ''
    port = 0
    remote_path = '/'
    
    try:
        s_list = sftp_path.split('//', 1)
        if (len(s_list) < 2):
            return tuple()
        s1 = s_list[1]
        
        s_list = s1.split('@', 1)
        if (2 != len(s_list)):
            return tuple()
        s0 = s_list[0]
        s1 = s_list[1]
        
        s_list = s0.split(':', 1)
        if (2 != len(s_list)):
            return tuple()        
        user = s_list[0]
        passwd = s_list[1]
        
        s_list = s1.split(':', 1)
        if (2 != len(s_list)):
            return tuple()
        host = s_list[0]
        s1 = s_list[1]
        
        s_list = s1.split('/', 1)
        if (len(s_list) < 2):
            return tuple()
        port = int(s_list[0])
        remote_path = remote_path + s_list[1]
        
        return (user, passwd, host, port, remote_path)
    except Exception as e:
        logging.error("parse sftp info fail: %s", e)
        return tuple()
    

class SFtpWrap:
    def __init__(self, host, port, username, passwd, timeout=10):
        t = paramiko.Transport((host,port))
        t.banner_timeout = timeout
        t.connect(username = username, password = passwd)
        self.sftp = paramiko.SFTPClient.from_transport(t) 
        
    def upload(self, remote):
        backup_ok = os.path.join(backup+"success/")
        backup_fail = os.path.join(backup+"fail/")
        if not os.path.exists(backup_ok):
            os.makedirs(backup_ok, 777)
        if not os.path.exists(backup_fail):
            os.makedirs(backup_fail, 777)
        if not mkdirs_remote(self.sftp,remote):
            logging.error("SFTP failed to create remote dir: %s", remote)
            return False
        while(1):
            for fpath in glob.glob(pattern):
                try:
                    fname = os.path.split(fpath)[1]
                    self.sftp.put(fpath,os.path.join(remote+fname))
                    logging.info("put ok: %s ==> %s@%s:%s", fpath, username, host, remote)
                    shutil.move(fpath,os.path.join(backup_ok+fname))    
                except Exception as e:
                    logging.error("SFTP put %s ==> %s@%s:%s failed. Err: %s", fpath, username, host, remote, e)
                    shutil.move(fpath,os.path.join(backup_fail+fname)) 
            time.sleep(1)
        return True
        
    def download(self, remote_path, local_path):
        try:
            self.sftp.get(remote_path, local_path)
            logging.info('SFTP download ok: %s', remote_path)
            return True
        except Exception as e:
            logging.error('SFTP download %s fail. Err: %s', remote_path, e)
            return False


class PlcInfo:
    def __init__(self):
        self.id = ''
        self.flag = ''  #特征库标识
        self.version = ''
        self.num = 0
        
    def parse_info(self, fname):
        l = fname.rsplit('_', 1)  #fname: snort_evt_20210817182033.tar.gz
        if 2 == len(l):
            self.flag = l[0]  #特征库标识 snort_evt
            self.id = l[0].replace('_', '.', 1)  #特征库ID snort.evt
            self.version = l[1]  #版本号 20210817182033    

    
class UpgradeCmd:
    def __init__(self, bathNo):
        self.bathNo = bathNo
        self.attr = UpgradeCmdAttr()
        self.dbs = []
  
    def parse_cmd(self, xml_path):
        if not os.path.exists(xml_path):
            logging.error('xml not exists: %s', xml_path)
            return False
        tree = ET.parse(xml_path)
        root = tree.getroot()
        self.attr.sid = root.attrib.get('sid', '')
        self.attr.type = int(root.attrib.get('type', 0))
        self.attr.timestamp = int(root.attrib.get('timestamp', 0))
        if self.attr.check():
            for elem in tree.iter(tag='db'):
                db = UpgradeCmdDb()
                db.id = elem.attrib.get('id', '')
                db.version = elem.attrib.get('version', '')
                db.path = elem.attrib.get('path', '')
                db.md5 = elem.attrib.get('md5', '')
                db.num = elem.attrib.get('num', 0)
                if db.check():
                    self.dbs.append(db)
                else:
                    logging.error("db in %s err: id=%s version=%s path=%s md5=%s num=%d", xml_path, db.id, db.version, db.path, db.md5, db.num)
            return True
        logging.error('parse_cmd fail: %s', xml_path)
        return False
    
    def do_download(self):
        if 0 == len(self.dbs):
            logging.error('download fail: dbs is empty')
            return
        
        for db in self.dbs:
            sftp_user, sftp_passwd, sftp_host, sftp_port, remote_path = parse_sftp_info(db.path)
            try:
                sftp = SFtpWrap(sftp_host, sftp_port, sftp_user, sftp_passwd)
                remote_fname = os.path.split(remote_path)[-1]  #文件名
                
                plc_info = PlcInfo()
                plc_info.num = db.num
                plc_info.parse_info(remote_fname)  
                
                file_name = self.bathNo + "+" + remote_fname  #下载时文件名加上 bathNo 前缀，方便EU生成升级结果文件
                local_path = os.path.join(g_cfg.download_to_dir, file_name)  #下载文件到指定目录
                
                if sftp.download(remote_path, local_path):
                    logging.info('download success: %s', db.path)
                    local_md5 = hashlib.md5(open(local_path,'rb').read()).hexdigest()
                    if db.check_md5(local_md5):
                        logging.info('check file md5 success: %s', db.path)
                        db.local_path = local_path
                        g_all_plc_info_dict[plc_info.id] = plc_info  # 有则覆盖
                        if 'config.list' == plc_info.id:
                            g_running_plc.parse(local_path, './runningCfg')
                    else:
                        db.upgrade_code = EnumUpgradeCode.E_FMT_ERR.value
                        logging.error('check file md5 fail: db.path=%s db.md5=%s local.md5=%s', db.path, db.md5, local_md5)
                        # os.remove(local_path)
                else:
                    db.upgrade_code = EnumUpgradeCode.E_DOWNLOAD_FAIL.value
                    logging.error('download fail: %s', db.path)
            except Exception as e:
                db.upgrade_code = EnumUpgradeCode.E_DOWNLOAD_FAIL.value
                logging.error('download %s fail: %s', db.path, e)
    
    def create_upgrade_result(self):
        dir = os.path.join(g_cfg.download_to_dir, 'upgrade')
        time.sleep(30)  # 为了让EU生成升级结果，此处等 30s, TODO 后续优化
        if not os.path.exists(dir):
            logging.error('get upgrade result timeout: bathNo=%s', self.bathNo)
            return
        
        doc = xml.dom.minidom.Document()
        root = doc.createElement('response')
        root.setAttribute('sid', g_cfg.dev_id)
        root.setAttribute('type', str(g_cfg.dev_type))
        root.setAttribute('timestamp', str(int(time.time())))
        root.setAttribute('vendorid', g_cfg.vendor_id)
        doc.appendChild(root)
        
        for db in self.dbs:
            db_node = doc.createElement('db')
            db_node.setAttribute('fileType', db.id)
            db_node.setAttribute('version', db.version)
            db_node.setAttribute('md5', db.md5)
            
            if -1 == db.upgrade_code:
                result_file = ''
                for code in EnumUpgradeCode:
                    result_file = db.local_path + '+' + str(code.value)
                    if os.path.exists(result_file):
                        db_node.setAttribute('code', code.value)
                        db_node.appendChild(doc.createTextNode(UpgradeCmd.upgrade_result_dict[code.value]))
                        break
                if 0 == len(result_file):  # 默认成功
                    db_node.setAttribute('code', EnumUpgradeCode.E_OK.value)
                    db_node.appendChild(doc.createTextNode(UpgradeCmd.upgrade_result_dict[0]))                    
            else:
                # 下载已经出错了
                db_node.setAttribute('code', db.upgrade_code)
                db_node.appendChild(doc.createTextNode(UpgradeCmd.upgrade_result_dict[db.upgrade_code]))
            root.appendChild(db_node)

        xml_path = os.path.join(dir, f'{self.bathNo}+upgradeResult.xml')
        tmp_xml_path = xml_path + '.tmp'
        with open(tmp_xml_path, 'w+', encoding='utf-8') as fp:
            doc.writexml(fp, indent='', addindent='\t', newl='\n', encoding='utf-8')
        os.rename(tmp_xml_path, xml_path)


class NamdReqHandler(BaseHTTPRequestHandler):
    def send_namd_response(self, retcode, msg):
        if 200 == retcode:
            logging.info(msg)
        else:
            logging.error(msg)
        self.send_response(retcode)
        #self.send_header('RetCode', retcode)
        self.send_header('Content-type', g_ct_json)
        content = {'Message' : msg}
        content = json.dumps(content).encode()
        self.send_header('Content-Length', len(content))
        self.send_header('Version', g_cfg.version)
        self.end_headers()
        self.wfile.write(content)
        
    def do_namd_post(self, post_type):
        auth = ''
        key = 'Authorization'
        if key in self.headers.keys():
            auth = self.headers.get(key)
        else:
            msg = f'Authorization in request headers is None'
            self.send_namd_reponse(500, msg)
            return
            
        l = auth.split(' ')
        if 2 != len(l):
            msg = f'Authorization in request headers err: {auth}'
            self.send_namd_reponse(500, msg)
            return
        auth = l[1]
        retcode, errstr = HttpOps.check_auth(auth)
        if 200 == retcode:
            devid = ''
            key = 'User-Agent'
            if key in self.headers.keys():
                devid = self.headers.get(key)
            else:
                key = 'user-agent'
                if key in self.headers.keys():
                    devid = self.headers.get(key)
            
            ctype = ''
            key = 'Content-Type'
            if key in self.headers.keys():
                ctype = self.headers.get(key)
                
            ctlen = 0
            key = 'Content-Length'
            if key in self.headers.keys():
                ctlen = int(self.headers.get(key))
                
            ver = ''
            key = 'Version'
            if key in self.headers.keys():
                ver = self.headers.get(key)
            
            bathNo = ''
            key = 'bathNo'
            if key in self.headers.keys():
                bathNo = self.headers.get('bathNo')
            
            bad = False
            body = ''
            
            err_set = set()
            err_set.add(devid != g_cfg.dev_id)
            err_set.add(0 == len(ctype))
            err_set.add(0 == ctlen)
            #err_set.add(ver != g_cfg.version)
            if (-1 == post_type):
                err_set.add(0 == len(bathNo))
            
            if any(err_set):
                logging.error('<%s> header err: devid=%s ctype=%s ctlen=%d bathNo=%s', self.path, devid, ctype, ctlen, bathNo)
                bad = True
            else:
                body = self.rfile.read(ctlen).decode('utf-8')
                if 0 == len(body):
                    bad = True
                    logging.error('read <%s> content fail: ctype=%s bathNo=%s', self.path, ctype, bathNo)
            if bad:
                self.send_namd_response(500, f'check {self.path} request header fail. bathNo={bathNo}')
                #elif 0 == post_type:
                #    self.send_namd_response(500, f'check request(/context/upgrade/report) header fail.')
            else:
                #self.send_header('Server', 'BaseHTTP')
                #now = time.strftime("%Y%m%d%H%M%S", time.localtime())
                #self.send_header('Date', now)
                msg = '200OK'
                if -1 == post_type:
                    msg = f'recv bathNo={bathNo} success'
                self.send_namd_response(200, msg)
                
                if -1 == post_type:
                    dir = './upgrade_cmd'
                    if not os.path.exists(dir):
                        os.makedirs(dir, 777)
                    xmlpath = f'{dir}/{bathNo}_{time.strftime("%Y%m%d%H%M%S")}.xml'
                    with open(xmlpath, 'w+') as outf:  
                        outf.write(body)  #将接收到的内容写入xml
                  
                    cmd = UpgradeCmd(bathNo)
                    cmd.parse_cmd(xmlpath)
                    cmd.do_download()
                    cmd.create_upgrade_result()
                #elif 1 == post_type:
                #    dir = './status_result'
                #    if not os.path.exists(dir):
                #        os.makedirs(dir, 777)
                #    xmlpath = f'{dir}/{time.strftime("%Y%m%d%H%M%S")}_status.xml'
                #    with open(xmlpath, 'w+') as outf:  
                #        outf.write(body)  #将接收到的内容写入xml
        else:
            self.send_namd_response(retcode, errstr)
    
    def do_POST(self):
        path = str(self.path)
        if path == "/update":
            self.do_namd_post(-1)
        #elif path == "/context/upgrade/report":
        #    dir = './upgrade_result'
        #    if not os.path.exists(dir):
        #        os.makedirs(dir, 777)
        #    self.do_namd_post(0)
        #elif path == "/context/statusreport":
        #    dir = './status_result'
        #    if not os.path.exists(dir):
        #        os.makedirs(dir, 777)
        #    self.do_namd_post(1)


#HTTPS://ip:port/upgrade/report
def upload_grade_result():
    headers={
    'Authorization':'',
    'Host':f'{g_cfg.upgrade_report_host}:{g_cfg.upgrade_report_port}',
    'User-Agent':g_cfg.dev_id,
    'Content-Type':g_ct_xml,
    'Content-Length':'',
    'Version':g_cfg.version,
    'bathNo':''
    }
    auth_token = HttpOps.make_auth_token(g_cfg.token)
    headers['Authorization'] = f'Basic {auth_token}'
    
    # 每 5s 扫描一次升级结果文件，并用 https post 上报
    url = f'https://{g_cfg.upgrade_report_host}:{g_cfg.upgrade_report_port}/upgrade/report'
    dir = os.path.join(g_cfg.download_to_dir, 'upgrade')
    for root, dirs, files in os.walk(dir):
        for f in files:
            if f.endswith('upgradeResult.xml'):
                bathNo = f.split('+')[0]
                headers['bathNo'] = bathNo
                xml_path = os.path.join(dir, f)
                headers['Content-Length'] = str(os.path.getsize(xml_path))
                post_ok = False
                ntry = 3
                while ntry > 0:
                    logging.info('grade result headers: %s', headers)
                    if HttpOps.https_post_file(url, headers, xml_path):
                        post_ok = True
                        break
                    ntry -= 1
                    time.sleep(1)
                if post_ok:
                    os.remove(xml_path)
        
    global grade_result_timer
    grade_result_timer = threading.Timer(10, upload_grade_result)
    grade_result_timer.start()


def get_netio_stat():
    key_info = psutil.net_io_counters(pernic=True).keys()  # 获取网卡名称
    recv = {}
    sent = {}
 
    for key in key_info:
        recv.setdefault(key, psutil.net_io_counters(pernic=True).get(key).bytes_recv)  # 各网卡接收的字节数
        sent.setdefault(key, psutil.net_io_counters(pernic=True).get(key).bytes_sent)  # 各网卡发送的字节数
 
    return key_info, recv, sent


def get_netio_rate():
    key_info, old_recv, old_sent = get_netio_stat()  # 上一秒收集的数据
    time.sleep(1)
    key_info, now_recv, now_sent = get_netio_stat()  # 当前所收集的数据
 
    net_in = {}
    net_out = {}
 
    for key in key_info:
        net_in.setdefault(key, (now_recv.get(key) - old_recv.get(key)) / 1024 / 1024)  # 接收速率 Mbit/s
        net_out.setdefault(key, (now_sent.get(key) - old_sent.get(key)) / 1024 / 1024) # 发送速率 Mbit/s
 
    return key_info, net_in, net_out

 
def get_host_ip():
    ip = '127.0.0.1'
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def create_dev_status(xml_path):
    #attribute
    doc = xml.dom.minidom.Document()
    root = doc.createElement('status')
    root.setAttribute('sid', g_cfg.dev_id)
    root.setAttribute('type', str(g_cfg.dev_type))
    root.setAttribute('timestamp', str(int(time.time())))
    root.setAttribute('vendorid', g_cfg.vendor_id)
    doc.appendChild(root)
    
    #db 
    for key,value in g_all_plc_info_dict.items():
        db_node = doc.createElement('db')
        db_node.setAttribute('id', str(value.id))
        db_node.setAttribute('version', value.version)
        db_node.setAttribute('num', str(value.num))
        root.appendChild(db_node)      
    
    #config
    cfg_node = doc.createElement('config')
    node = doc.createElement('stfreq')
    node.appendChild(doc.createTextNode(f'{g_running_plc.stfreq}'))
    cfg_node.appendChild(node)
    node = doc.createElement('devtype')
    node.appendChild(doc.createTextNode(f'{g_cfg.dev_type}'))
    cfg_node.appendChild(node)
    node = doc.createElement('softver')
    node.appendChild(doc.createTextNode(f'{g_cfg.version}'))
    cfg_node.appendChild(node)
    node = doc.createElement('vender')
    node.appendChild(doc.createTextNode(f'{g_cfg.vendor_id}'))
    cfg_node.appendChild(node)
    node = doc.createElement('devip')
    ip = get_host_ip()
    node.appendChild(doc.createTextNode(f'{ip}'))
    cfg_node.appendChild(node)
    
    root.appendChild(cfg_node)
    
    #sysinfor
    percents = psutil.cpu_percent(interval=0, percpu=True)
    sys_node = doc.createElement('sysinfor')
    #sysinfor-CPU
    for i in range(psutil.cpu_count()):
        node = doc.createElement('CPU')
        node.setAttribute('id', str(i))
        node.appendChild(doc.createTextNode(f'{percents[i]:.2f}'))
        sys_node.appendChild(node)
    #sysinfor-MEM
    node = doc.createElement('MEM')
    mem = (psutil.virtual_memory().percent) / 100.00;
    node.appendChild(doc.createTextNode(f'{mem:.2f}'))  #内存利用率
    sys_node.appendChild(node)
    #sysinfor-HDISK
    dk = psutil.disk_usage('/')
    dk_used = dk.used / dk.total
    node = doc.createElement('HDISK')
    sys_node.appendChild(node)
    node.appendChild(doc.createTextNode(f'{dk_used:.2f}'))
    #sysinfor-IF_THRPUT
    key_info, net_in, net_out = get_netio_rate()
    for key in key_info:
        node = doc.createElement('IF_THRPUT')
        node.setAttribute('name', key)
        mbits = net_in[key]
        node.appendChild(doc.createTextNode(f'{mbits:.2f}'))  #暂时只记录输入流量速率
        sys_node.appendChild(node)
    root.appendChild(sys_node)

    with open(xml_path, 'w+', encoding='utf-8') as fp:
        doc.writexml(fp, indent='', addindent='\t', newl='\n', encoding='utf-8')


def upload_dev_status():
    headers={
    'User-Agent':g_cfg.dev_id,
    'Content-Type':g_ct_xml,
    'Version':g_cfg.version,
    'Authorization':''
    }
    #https
    url = f'https://{g_cfg.status_report_host}:{g_cfg.status_report_port}/statusreport'
    auth_token = HttpOps.make_auth_token(g_cfg.token)
    headers['Authorization'] = f'Basic {auth_token}'
    xml_path = os.path.join(g_cfg.dev_status_dir, 'devStatus.xml')
    create_dev_status(xml_path)
    HttpOps.https_post_file(url, headers, xml_path)

    global dev_status_timer
    dev_status_timer = threading.Timer(g_running_plc.stfreq, upload_dev_status)
    dev_status_timer.start()
    
    
def start_client():
    logging.info('starting client...')
    upload_grade_result()
    upload_dev_status()
    logging.info('client statred')


def start_server():
    addr = ('', g_cfg.port)
    logging.info('server port: %d', g_cfg.port)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain("namdHttpd.pem","namdHttpd.key") # openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout key.pem -out cert.pem
    httpd = HTTPServer(addr, NamdReqHandler)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    httpd.timeout = 60
    logging.info('Starting namdHttpd...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.critical('Stopping namdHttpd...')


def bind_cpu(pid, cpu):
    if 0 == cpu:
        logging.error('binding to CPU#0 is not allowed!')
        return False
    cpu_set = set()
    cpu_set.add(cpu)
    os.sched_setaffinity(pid, cpu_set)
    return True


def init_logger():
    namd_logger = logging.getLogger()
    namd_logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s: [%(asctime)s] %(message)s')
    filehandler = handlers.TimedRotatingFileHandler("./namdHttpd.log", when='d', interval=1, backupCount=7)#每 1(interval) 天(when) 重写1个文件,保留7(backupCount) 个旧文件；when还可以是Y/m/H/M/S
    filehandler.suffix = "namdHttpd_%Y%m%d%H%M%S.log"  #历史文件名
    filehandler.setFormatter(formatter)
    namd_logger.addHandler(filehandler)
    

if __name__ == "__main__":

    wd = os.path.abspath(os.path.dirname(sys.argv[0]))
    os.chdir(wd)
    logging.info("current working dir: %s", wd)
    
    init_logger()
    
    global g_cfg
    g_cfg = GlobalConf()
    if not g_cfg.parse('./conf.ini'):
        logging.error('parse conf.ini fail! Program refused to run!!')
        sys.exit()
    
    if not bind_cpu(0, g_cfg.cpu):
        logging.error('bind cpu fail! Program refused to run!!')
        sys.exit()
        
    global g_ct_xml
    g_ct_xml = 'application/xml; charset=utf-8'
    global g_ct_json
    g_ct_json = 'application/json; charset=utf-8'
        
    global g_running_plc
    g_running_plc = RunningCfgPlc()
    global g_all_plc_info_dict
    g_all_plc_info_dict = {}
    
    #创建进程，接收升级指令HTTPS(作为服务端，并下载升级指令中的策略文件)
    serv = Process(target=start_server)
    serv.start()
    bind_cpu(serv.pid, g_cfg.cpu)
    
    #创建进程，反馈升级结果HTTP、状态上报HTTPS(作为客户端)
    client = Process(target=start_client)
    client.start()
    bind_cpu(client.pid, g_cfg.cpu)
    
    serv.join()
    client.join()

```
