#coding:utf-8
from __future__ import print_function
import os
import shutil
import sys
import socket
import logging
import json
import time
import getpass
sys.path.append(os.path.dirname(os.getcwd()))
sys.path.append("venv")
# sys.path.append("C:\\Users\\zoujiaying\\Downloads\\whole_unit_test_v1.0.0.1\\whole_unit_test\\")
from config import ZLIMS_HOSTNAME, ZLIMS_PORT, MQ_PORT, ZLIMS_CONFIG, MOM_CONFIG, call_task_interval, ZLIMS_PRO_PORT, CREATE_DNB_SAMPLE_URL
import zipfile
import ctypes
sys.path.append(os.path.join(os.path.dirname(os.getcwd()), "mypackages", "venv"))
print(sys.path)
import requests
from requests.auth import HTTPBasicAuth

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

bot_id = sys.argv[1]    #这里参数0是脚本本身，参数1--n为传入的参数。
# bot_id = 'DNBSEQ-G50'
file_Name = 'BGI.zip'   # 配置文件必须打包为BGI.zip,并放置在whole_unit_test\ 目录下。
pc_name = socket.gethostname()
user_name = getpass.getuser()

# 将配置文件拷贝至C盘根目录（假设配置文件放置在whole_unit_test目录下，即whole_unit_test\BGI.zip）
def copy_config_file(file_Name):
    source_dir = os.getcwd()
    # source_dir = os.path.dirname(os.getcwd())
    # print(source_dir+'\\'+file_Name)
    try:
        shutil.copy(os.path.join(source_dir, file_Name), os.path.join("C:\\", file_Name))
        print("File copied successfully.....")
        return True
    except IOError as e:
        print("Unable to copy file. %s" % e)
        return False
    except:
        print("Unexpected error:", sys.exc_info())
        return False
   
def unzip_file(file_Name,target_dir):
    source_dir = os.getcwd()
    f = zipfile.ZipFile(source_dir+'\\'+file_Name,'r')
    for file in f.namelist():
        f.extract(file,target_dir)

    

# 发送请求到系统
ZLIMS_APIS = {
    "preparement": {
        "method": "POST",
        "url": "/zlims/resources/instance/"
    }
}

payload = {
	"part_number": "%s" % bot_id,
	"serial_number": pc_name,
	"metadata": {
		"instrument_status": "Idle",
		"basecall_version": "1.0.0.0",
		"mapped_instrument_status": "Idle",
		"control_software_version": "1.5.0.1283"
	}
}


class Prepare_Test:
    def __init__(self):
        self.logger = logging.getLogger("ZLIMS")
        self.zlims_host = ZLIMS_HOSTNAME
        self.zlims_port = ZLIMS_PORT
        self.API = 'http://%s:%s' % (ZLIMS_HOSTNAME, ZLIMS_PORT)
        self.AUTH = HTTPBasicAuth(ZLIMS_CONFIG["username"], ZLIMS_CONFIG["password"])

    def callZlimsApi(self, api_name, payload={}, **kwargs):
        api_info = ZLIMS_APIS.get(api_name)
        add_to_url = kwargs.get("add_to_url")
        format_to_url = kwargs.get("format_to_url")
        if api_info is None:
            self.logger.error("Unknow api name: %s" % api_name)
            return False
        else:
            try:
                method = api_info["method"]
                url = api_info["url"]
                url = '%s%s' % (self.API, url)
                if add_to_url:
                    url = "%s%s" % (url, add_to_url)
                if format_to_url:
                    url = url.format(format_to_url)
                time.sleep(call_task_interval)
                headers = {'content-type': 'application/json'}
                response = requests.request(method, url, json=payload,
                                            headers=headers, auth=self.AUTH)
                if response.status_code >= 300:
                    logging.error("Url: " + url + "\n" + str(payload))
                    print(response.text)
                    msg = ('Call the ZLIMS (' + api_name
                                + ') API Failed.  status code '
                                + str(response.status_code)
                                + "\n" + response.text)
                    logging.error(msg)
                    # raise Exception(str(msg))
                else:
                    if response.status_code == 204:
                        return None
                    else:
                        response.encoding = 'utf-8'
                        return json.loads(response.text)
            except Exception as e:
                logging.error("Url: " + url + "\n" + str(payload))
                msg = 'Call the ZLIMS (' + api_name + ') API Failed.' + str(e)
                logging.error(msg)
                # raise Exception(str(msg))
                return False

def main():
    if copy_config_file(file_Name):
        unzip_file(file_Name,'C:\\')
        os.remove('C:\\BGI.zip')
    else:
        print("Error: Copy Config files Error")
    print("Create instrument instance...")
    app = Prepare_Test()
    app.callZlimsApi("preparement",payload)

main()
