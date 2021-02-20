import sys
import logging
import requests
from requests.auth import HTTPBasicAuth
import json
from stompest.config import StompConfig
from stompest.protocol import StompSpec
from stompest.sync import Stomp
import random
import math
from config import ZLIMS_HOSTNAME, ZLIMS_PORT, MQ_PORT, ZLIMS_CONFIG, MOM_CONFIG, call_task_interval, ZLIMS_PRO_PORT, CREATE_DNB_SAMPLE_URL
import time
import datetime
import os
ZLIMS_APIS = {
    "create_resource": {
        "method": "POST",
        "url": "/zlims/resources/instance/"
    },
    "update_resource": {
        "method": "POST",
        "url": "/zlims/resources/{}/update/"
    },
    "delete_resource": {
        "method": "POST",
        "url": "/zlims/resources/delete/"
    },
    "get_resource": {
        "method": "GET",
        "url": "/zlims/resources/instance/"
    },
    "start_task": {
        "method": "POST",
        "url": "/zlims/workflow/taskinstance/"
    },
    "update_task": {
        "method": "POST",
        "url": "/zlims/workflow/taskinstance/{}/update/"
    },
    "complete_task": {
        "method": "POST",
        "url": "/zlims/workflow/taskinstance/{}/complete/"
    },
    "get_task": {
        "method": "GET",
        "url": "/zlims/workflow/taskinstance/"
    },
    "get_task_detail": {
        "method": "GET",
        "url": "/zlims/workflow/taskinstance/{}/"
    },
    "get_zlims_product": {
        "method": "GET",
        "url": "/zlims/utils/get_zlims_product"
    },
    "get_resource_type": {
        "method": "GET",
        "url": "/zlims/resources/type"
    },
    "get_drop_down_option": {
        "method": "POST",
        "url": "/zlims/lookupValues/getDropdownOption/"
    },
    "get_instrument_report": {
        "method": "GET",
        "url": "/zlims/reports/instruments/"
    },
    "get_version": {
        "method": "GET",
        "url": "/zlims/utils/version/"
    },
    "get_barcode_info": {
        "method": "GET",
        "url": "/zlims/pipeline/tools/getBarcodeInfo/"
    }
}

log_file = os.path.join(sys.path[0], 'run.log')

logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO, filename=log_file,
            filemode='a',)


def datetime_format(datetime_obj):
    return datetime_obj.strftime("%Y-%m-%dT%H:%M:%SZ")


def datetime_format_seq(datetime_obj):
    return datetime_obj.strftime("%Y-%m-%d %H:%M:%SZ")

class ZLIMSClient:

    def __init__(self):
        self.logger = logging.getLogger("ZLIMS")
        self.zlims_host = ZLIMS_HOSTNAME
        self.zlims_pro_port = ZLIMS_PRO_PORT
        self.API = 'http://%s:%s' % (ZLIMS_HOSTNAME, ZLIMS_PORT)
        self.AUTH = HTTPBasicAuth(ZLIMS_CONFIG["username"], ZLIMS_CONFIG["password"])

    def create_dnb_payload(self, serial_number, samples):
        payload = """
[
  {
    "serial_number": "%s",
    "part_number": "xx-DNB-xx",
    "metadata": {
        "samples": %s
    }
  }
]
""" % (serial_number, json.dumps(samples))
        return payload

    def create_machine_payload(self, serial_number, part_number):
        payload = """
[
  {
    "serial_number": "%s",
    "part_number": "%s",
    "metadata": {
        "basecall_version": "0.0.0.1",
		"control_software_version": "0.0.0.1"
    }
  }
]
""" % (serial_number, part_number)
        return payload

    def create_delete_dnb_payload(self, serial_number):
        return """
[
  {
    "serial_number": "%s",
    "part_number": "xx-DNB-xx"
  }
]
""" % serial_number

    def create_start_library_payload(self, machine_id, library_id, samples):
        columns = "A B C D E F G H".split(" ")
        i = 0
        j = 1
        for sample in samples:
            if j > 12:
                j = 1
                i += 1
            pos = columns[i] + str(j)
            sample["well"] = pos
            j += 1
        return """
{
    "task_id": "library",
    "task_config_id": "library",
    "operator_id": "unit_test",
    "machine_id": "%s",

    "resources": [],
    "inputs": {
        "lib_id": "%s",
        "samples": %s
    }
}
""" % (machine_id, library_id, json.dumps(samples))

    def create_complete_library_payload(self, samples):
        new_sample = []
        for sample in samples:
            concentration = random.randint(0, 100)
            new_sample.append({
                "barcode_id": sample["barcode_id"],
                "concentration": concentration
            })
        return """
{
    "completion_status": "success",
    "inputs": {
        "samples": %s
    }
}
""" % json.dumps(new_sample)


    def create_start_pool_payload(self, machine_id, library_id, pool_id):

        return """
{
    "task_id": "pool",
    "task_config_id": "pool",
    "operator_id": "unit_test",
    "machine_id": "%s",

    "resources": [],
    "inputs": {
        "pooled_library_id": "%s",
        "pool_list":[{
            "lib_id" : "%s"
        }]
    }
}
""" % (machine_id, pool_id, library_id)

    def create_complete_pool_payload(self, library_id, samples):
        new_sample = []
        for sample in samples:
            volume = random.randint(0, 100)
            new_sample.append({
                "barcode_id": sample["barcode_id"],
                "volume": volume,
                "pool_status": "success"
            })
        return """
{
    "completion_status": "success",
    "inputs": {
        "pool_list":
        [
          {
            "lib_id":"%s",
            "pool_status":"success",
            "samples": %s
          }
        ]
    }
}
""" % (library_id, json.dumps(new_sample))

    def create_start_make_dnb_payload(self, machine_id, pool_id, dnb_id):

        return """
{
    "task_id": "make_dnb",
    "task_config_id": "make_dnb",
    "operator_id": "unit_test",
    "machine_id": "%s",

    "resources": [],
    "inputs": {
        "pooled_library_id": "%s",
        "dnb_id":"%s"
    }
}
""" % (machine_id, pool_id, dnb_id)

    def create_complete_make_dnb_payload(self):
        concentration = random.randint(0, 100)
        return """
{
    "completion_status": "success",
    "inputs": {
        "concentration":"%s",
        "make_dnb_status":"success"
    }
}
""" % concentration


    def create_start_load_dnb_payload(self, lanes, flowcell_sn, machine_id):
        machine_str = ""
        if machine_id and machine_id != ',':
            machine_str = '"machine_id": "%s",' % machine_id
        return """
{
  "task_id": "load_dnb",
  "task_config_id": "load_dnb",
  %s
  "operator_id": "unit_test",
  "resources": [
  ],
  "inputs": {
    "flowcell_id": "%s",
    "load_type": "manual",
    "lanes": %s
  }
}
""" % (machine_str, flowcell_sn, json.dumps(lanes))

    def create_update_load_dnb_payload(self):
        return """
{
  "inputs": {
    "LoadDNB_completion_time": "2019-01-01 10:20:11"
  }
}
"""

    def create_complete_load_dnb_payload(self):
        return """
{
  "completion_status": "success",
  "inputs": {
    "load_dnb_status": "success"
  }
}
"""

    def create_start_sequencing_payload(self, sequencing_mode, flowcell_sn, machine_id):
        if sequencing_mode == "PE":
            input_detail = """
        "sequencing_type": "PE",
        "read2_cycle_count": 50"""
        else:
            input_detail = """
        "sequencing_type": "SE"
"""
        machine_str = ""
        if machine_id and machine_id != ',':
            machine_str = '"machine_id": "%s",' % machine_id
        if machine_id and machine_id.find("DNBSEQ-T7") != -1:
            input_detail = """%s,
        "is_sync_cal": "true"
""" % input_detail

        return """
{
    "task_id": "sequencing",
    "task_config_id": "sequencing",
    %s
    "association_id": "%s",
    "operator_id": "unit_test",
    "resources": [
    ],
    "inputs":
      {
        "flowcell_id": "%s",
        "version":"V2",
        "read1_cycle_count":1,%s
      }
}
""" % (machine_str, flowcell_sn, flowcell_sn, input_detail)

    def create_update_sequencing_payload(self, lane_id, cycle_id):
        payload = '''
        {
           "inputs":{
              "command":"update_qc_data",
              "qc_data":[
                 {
                    "lane_id":"%(lane_id)s",
                    "cycle_id":%(cycle_id)s,
                    "QC_AVG_FIT":"%(FIT)s",
                    "QC_AVG_BIC":"%(BIC)s",
                    "QC_AVG_ACC_GRR":"%(GRR)s",
                    "QC_AVG_ESR":"%(ESR)s",
                    "QC_AVG_SNR_A":"%(SNR_A)s",
                    "QC_AVG_SNR_T":"%(SNR_T)s",
                    "QC_AVG_SNR_C":"%(SNR_C)s",
                    "QC_AVG_SNR_G":"%(SNR_G)s",
                    "QC_AVG_SIG_A":"%(SIG_A)s",
                    "QC_AVG_SIG_T":"%(SIG_T)s",
                    "QC_AVG_SIG_C":"%(SIG_C)s",
                    "QC_AVG_SIG_G":"%(SIG_G)s"
                 }
              ]
           }
        }
        '''
        payload = payload % {
    "lane_id": lane_id,
    "cycle_id": cycle_id,
    "FIT": int(math.cos(cycle_id*random.random()/45)*98)/100,
    "BIC": int(math.cos(cycle_id*random.random()/80)*9923)/100,
    "GRR": int(math.cos(cycle_id*random.random()/45)*100)/100,
    "ESR": int(math.cos(cycle_id*random.random()/45)*95)/100,
    "SNR_A": int(math.cos(cycle_id*random.random()/45)*611)/100,
    "SNR_T": int(math.cos(cycle_id*random.random()/45)*562)/100,
    "SNR_C": int(math.cos(cycle_id*random.random()/45)*605)/100,
    "SNR_G": int(math.cos(cycle_id*random.random()/45)*596)/100,
    "SIG_A": int(math.cos(cycle_id*random.random()/80)*400534)/100,
    "SIG_T": int(math.cos(cycle_id*random.random()/80)*415600)/100,
    "SIG_C": int(math.cos(cycle_id*random.random()/80)*420200)/100,
    "SIG_G": int(math.cos(cycle_id*random.random()/80)*410500)/100
}
        return payload

    def create_update_write_fastq(self, lanes):
        fastq_data = []
        for lane in lanes:
            now = datetime.datetime.utcnow()
            start_time = now - datetime.timedelta(minutes=random.randint(10, 1000))
            fastq_data.append(
                {
                 "lane_id": lane,
                 "copying_start_time": datetime_format_seq(start_time),
                 "writing_start_time": datetime_format_seq(start_time),
                 "writing_completion_time": datetime_format_seq(now),
                 "writing_completion_status": "success",
                 "copying_completion_time": datetime_format_seq(now),
                 "copying_status": "success"
               })
        return """
{
   "inputs":
   {
     "command":"update_fastq_data",
     "cycle_completion_time":"%s",
     "cycle_completion_status":"success",
     "fastq_data": %s
   }
}
""" % (datetime_format(datetime.datetime.utcnow()), json.dumps(fastq_data))

    def create_complete_sequencing_payload(self, lanes, samples, sequencing_mode):
        samples_data = []
        lanes_data = []
        reads_keys = ['Read1', 'Total Read']
        sample_read_keys = ['PhredQual', 'ReadNum', 'BaseNum', 'N_Count%', 'GC%', 'Q10%', 'Q20%', 'Q30%', 'EstErr%']
        if sequencing_mode == 'PE':
            reads_keys.append('Read2')
        for sample in samples:
            samples_data.append({
                "barcode_id": sample["barcode_id"],
                "subject_id": sample["subject_id"],
                "SampleFqStatisticsMap": self.create_qc_data(reads_keys, sample_read_keys)
            })

        SummaryMap = [
                            {
                                "SoftwareVersion": "0.5.4.148"
                            },
                            {
                                "TemplateVersion": "0.7.4"
                            },
                            {
                                "Reference": "NULL"
                            },
                            {
                                "CycleNumber": "210"
                            },
                            {
                                "ChipProductivity(%)": "80.55"
                            },
                            {
                                "ImageArea": "432"
                            },
                            {
                                "TotalReads(M)": "372.7211111111111111111"
                            },
                            {
                                "Q30(%)": "90.3411111111"
                            },
                            {
                                "SplitRate(%)": "96.601111111111111"
                            },
                            {
                                "Lag1(%)": "0.20"
                            },
                            {
                                "Lag2(%)": "0.34"
                            },
                            {
                                "Runon1(%)": "0.08"
                            },
                            {
                                "Runon2(%)": "0.17"
                            },
                            {
                                "ESR(%)": "80.551111111111"
                            },
                            {
                                "MaxOffsetX": "15.57"
                            },
                            {
                                "MaxOffsetY": "8.80"
                            },
                            {
                                "InitialOffsetX": "3.46"
                            },
                            {
                                "InitialOffsetY": "2.33"
                            },
                            {
                                "RecoverValue(A)": "2.88"
                            },
                            {
                                "RecoverValue(C)": "2.93"
                            },
                            {
                                "RecoverValue(G)": "2.60"
                            },
                            {
                                "RecoverValue(T)": "2.53"
                            },
                            {
                                "RecoverValue(AVG)": "2.73"
                            }
                        ]

        for lane in lanes:
            lanes_data.append({
                "lane_id": lane,
                "SummaryMap": SummaryMap,
                "LaneFqStatisticsMap": self.create_qc_data(reads_keys, sample_read_keys),
                "samples": samples_data
            })
        payload = """
{
  "completion_status":"success",
  "inputs":{
    "run_id":"test",
    "copying_status":"success",
    "sequencing_data_path":"E:\\\\SaveData",
    "lanes": %s
  }
}
""" % json.dumps(lanes_data)
        return payload

    def create_qc_data(self, first_keys, keys):
        read_datas = []
        for k in first_keys:
            read_data = {k: []}
            for k1 in keys:
                read_data[k].append({k1: random.randint(100, 1000000)})
            read_datas.append(read_data)
        return read_datas

    def create_start_upload_payload(self, lanes, flowcell_sn, rsync_host, upload_path, machine_id):
        machine_str = ""
        if machine_id and machine_id != ',':
            machine_str = '"machine_id": "%s",' % machine_id
        return """
{
    "task_id" : "upload_fastq",
    "task_config_id" : "upload_fastq",
    %s
    "operator_id": "unit_test",
    "resources": [],
    "inputs":
      {
        "remote_ip":"%s",
        "remote_root_path" :"%s",
        "flowcell_id" : "%s",
        "lanes" : %s
    }
}
""" % (machine_str, rsync_host, upload_path, flowcell_sn, json.dumps(lanes))

    def create_update_upload_payload(self, lanes, upload_path):
        fastq_files = []
        for lane in lanes:
            fastq_files.append({
                "lane_id": lane,
                "path": "%s/%s" % (upload_path, lane),
                "copying_status": "success"
            })
        return """
{
    "inputs":
    {
        "fastq_files" :%s
    }
}
""" % json.dumps(fastq_files)

    def create_complete_upload_payload(self):
        return """
{
  "completion_status":"success",
  "inputs":
  {
    "copying_status":"success"
  }
}
"""


    def callZlimsProImportDnbSample(self, excel):
        try:
            url = "http://%s:%s%s" % (self.zlims_host, self.zlims_pro_port, CREATE_DNB_SAMPLE_URL)
            formdata = {
                'inputSampleExcel': (open(excel, 'rb'))
            }
            headers = {
                "content": "multipart/form-data; boundary=<calculated when request is sent>"
            }
            response = requests.request("POST", url, files=formdata, headers=headers)
            if response.status_code == 404:
                url = "http://%s:%s%s" % (self.zlims_host, self.zlims_pro_port, CREATE_DNB_SAMPLE_URL)
                response = requests.request("POST", url, files=formdata, headers=headers)
            response.encoding = 'utf-8'
            if response.status_code >= 300:
                logging.error("Url: " + url + "\n" + str(excel))
                msg = 'Call the ZLIMSPro import dnb sample API Failed.\n Response text: %s' % response.text
                logging.error(msg)
                raise Exception(str(msg))
            text = json.loads(response.text)
            if text.get("code") != 0:
                logging.error("Url: " + url + "\n" + str(excel))
                msg = 'Call the ZLIMSPro import dnb sample API Failed. %s' % text.get("msg")
                logging.error(msg)
                raise Exception(str(msg))
                return False
            return text

        except Exception as e:
            logging.error("Url: " + url + "\n" + str(excel))
            msg = 'Call the ZLIMSPro import dnb sample API Failed.' + str(e)
            logging.error(msg)
            raise Exception(str(msg))
            return False


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
                response = requests.request(method, url, data=payload,
                                            headers=headers, auth=self.AUTH)
                if response.status_code >= 300:
                    logging.error("Url: " + url + "\n" + str(payload))
                    msg = ('Call the ZLIMS (' + api_name
                                + ') API Failed.  status code '
                                + str(response.status_code)
                                + "\n" + response.text)
                    logging.error(msg)
                    raise Exception(str(msg))
                    return False
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
                raise Exception(str(msg))
                return False


ZLIMS_MOM_TOPICS = {
    "task_create": "/topic/Task",
    "task_start": "/topic/Task",
    "task_update": "/topic/Task",
    "task_complete": "/topic/Task",
}

class MqClient:

    def __init__(self):
        self.url = "tcp://%s:%s" % (ZLIMS_HOSTNAME, MQ_PORT)
        self.config = StompConfig(self.url, login=MOM_CONFIG["username"], passcode=MOM_CONFIG["password"])
        self.logger = logging.getLogger("MqClient")
        self.client = Stomp(self.config)
        self.is_daemon = False
        self.message = None
        self.messages = []

    def connect(self):
        try:
            self.client.connect()
        except Exception as e:
            self.logger.error(str(e))
            return None
        return self.client

    def disconnect(self):
        try:
            self.client.disconnect()
        except Exception as e:
            self.logger.error(str(e))

    def publish(self, payload, topic_name):
        """ publishes a single message """
        destination = ZLIMS_MOM_TOPICS.get(topic_name)
        if destination:
            try:
                self.client.send(destination, payload.encode())
                return True
            except Exception as e:
                self.logger.error(str(e))
                return False
        else:
            self.logger.error("Unknow topic name: %s" % topic_name)
            return False

    def subscribe(self, topic):
        destination = topic
        if destination:
            try:
                token = self.client.subscribe(destination, {StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL})
                if self.client.canRead(5):
                    frame = self.client.receiveFrame()
                    self.client.ack(frame)
                    message = frame.body.decode('utf-8')
                    self.client.unsubscribe(token)
                    return message
                else:
                    self.client.unsubscribe(token)
                    return False
            except Exception as e:
                self.logger.error(str(e))
                self.client.unsubscribe(token)
                return False

    def clear_messages(self):
        for mom in self.messages:
            self.logger.info(str(mom))
        self.messages = []

    def stop_subscribe_daemon(self):
        self.is_daemon = False

    def subscribe_daemon(self, topic_name):
        self.is_daemon = True
        self.clear_messages()
        while self.is_daemon:
            message = self.subscribe(topic_name)
            if message:
                self.messages.append(message)
