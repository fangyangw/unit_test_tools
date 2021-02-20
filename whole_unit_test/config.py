TEST_PRODUCTS = [
  # "WGS",
  # "WES",
  "PFI",
  # "BFI",
  # "BFI-TB",
  # "HMBI",
  # "NIPT",
  # "PGS",
  # "MGAP",
  # "MGAP_Assembly",
  # "stLFR-reSeq",
  # "ATOPlex SARS-CoV-2",
  # "MGI-SARS-CoV-2",
  # "FIS",
  # "RNA-Seq_basic_pipeline",
  # "scRNA_Seq",
]

ZLIMS_HOSTNAME = "172.16.36.7"

TEST_SEQUENCING_MODES = [
  "PE",
  # "SE"
]

# ZLIMS Pro language, value in ['cn', 'en']
TEST_LANGUAGE = 'en'
ZLIMS_PRO_PORT = "80"
CREATE_DNB_SAMPLE_URL = "/sample/apisampleListFileUpload"

TEST_SAMPLE_NUMBER = 1
# NIPT, MGAP only support >= 2 samples, if config this option, will ignore TEST_SAMPLE_NUMBER
ONLY_SUPPORT_MORE_SAMPLE_PRODUCTS = ['NIPT', 'MGAP', "FIS"]
# NIPT, PGS only support SE, if config this option, will ignore TEST_SEQUENCING_MODES
ONLY_SUPPORT_SE_PRODUCTS = ['NIPT', 'PGS', "FIS"]
# if config this option, will ignore TEST_SEQUENCING_MODES
ONLY_SUPPORT_PE_PRODUCTS = []

# Please make sure your installation path is correct. If your flag path is modified, please configure the corresponding path in the wdl file
WRITE_FASTQ_WDL_PATH = "/storeData/ztron/apps/WDL_Install/wdl/write_fastq.workflow.wdl"

ZLIMS_PORT = "8000"
MQ_PORT = "61613"

ZLIMS_CONFIG = {
  "username": "user",
  "password": "123"
}

MOM_CONFIG = {
  "username": "admin",
  "password": "admin"
}

CHECK_INSTRUMENT_CURRENT_STATUS = False
CHECK_RSYNC_STATUS = True
CHECK_TASK_MOM = True
call_task_interval = 1

TEST_CAL_FILE = "/storeData/pipeline/test_fq/write_fastq"
basecall_uid = 1001
basecall_gid = 1001
