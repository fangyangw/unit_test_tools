#coding: utf-8
import sys
import os
sys.path.append(os.path.join("mypackages", "venv"))
import unittest
from mypackages.zlims_tools import ZLIMSClient
import uuid
import threading
import json
import re
from mypackages.BSTestRunner import BSTestRunner
import subprocess
from config import TEST_SAMPLE_NUMBER, TEST_PRODUCTS, TEST_SEQUENCING_MODES, CHECK_TASK_MOM, ONLY_SUPPORT_MORE_SAMPLE_PRODUCTS, ONLY_SUPPORT_SE_PRODUCTS, ONLY_SUPPORT_PE_PRODUCTS
from mypackages.tools import WholePipelineTest, notification_console, get_analysis_time

dnb_prefix = "dnb_unit_test"
current_product = ""
#IS_T7 = False

def update_config_dnb_id(current_id):
    context = ''
    with open(os.path.join(sys.path[0], "config.py"), 'r') as fh:
        for line in fh.readlines():
            if line.startswith('current_test_id'):
                context += "current_test_id = %s\n" % current_id
            else:
                context += line
    with open(os.path.join(sys.path[0], "config.py"), 'w') as fh:
        fh.write(context)


class PipelineTest(unittest.TestCase):
    last_test_status = True

    def tearDown(self):
        notification_console("Info: complete test: %s" % self._testMethodName)

    def setUp(self):
        self.pipeline_test_tools = pipeline_test_tools
        notification_console("Info: start run test: %s" % self._testMethodName)

    def _common_run(self, test_func, error_reason="Error: got an exception."):
        if not self.last_test_status:
            self.skipTest(u'skip because last step error')
        status = True
        try:
            test_func()
        except Exception as e:
            status = False
            print(str(e))
            PipelineTest.last_test_status = False
        self.assertTrue(status, error_reason)

    def _test_instrument_config(self):
        if IS_T7:
            self.pipeline_test_tools.get_machine_id_for_T7()
        else:
            self.pipeline_test_tools.get_machine_id()
        self.pipeline_test_tools.check_machine_config()

    def test_instrument_config(self):
        self._common_run(self._test_instrument_config, "Error: can not get instrument config.")

    def _test_dca_status(self):
        self.pipeline_test_tools.check_mom_service_status()
        self.pipeline_test_tools.check_dca_status()

    def test_dca_status(self):
        self._common_run(self._test_dca_status, "Error: DCA status is wrong.")

    def _test_mom_status(self):
        self.pipeline_test_tools.check_mom_service_status()

    def test_mom_status(self):
        self._common_run(self._test_mom_status, "Error: can not connect ZLIMS MOM")

    def _test_create_dnb(self):
        self.pipeline_test_tools.import_dnb_sample_to_lims(test_sample_number)
        # self.pipeline_test_tools.create_samples(TEST_SAMPLE_NUMBER)
        # self.pipeline_test_tools.create_library_task()
        # self.pipeline_test_tools.create_pool_task()
        # self.pipeline_test_tools.create_make_dnb_task()

    def test_create_dnb(self):
        self._common_run(self._test_create_dnb, "Error: can not do create dnb.")

    def _test_create_dnb_manual(self):
        self.pipeline_test_tools.delete_dnb()
        self.pipeline_test_tools.create_dnb()

    def test_create_dnb_manual(self):
        self._common_run(self._test_create_dnb_manual, "Error: can not do create dnb.")

    def _test_load_dnb_task(self):
        if CHECK_TASK_MOM:
            self.pipeline_test_tools.start_listen_mq()
        self.pipeline_test_tools.create_load_dnb_task()

    def test_load_dnb_task(self):
        self._common_run(self._test_load_dnb_task, "Error: can not do load dnb task.")

    def _test_sequencing_task(self):
        self.pipeline_test_tools.create_sequencing_task()
        if IS_T7:
            notification_console("Info: Write fastq task created successfully, go to the bio-pass page to see if the task started properly.")
            self.pipeline_test_tools.stop_listen_mq()

    def test_sequencing_task(self):
        self._common_run(self._test_sequencing_task, "Error: can not do sequencing task.")

    def _test_upload_task(self):
        self.pipeline_test_tools.create_upload_task()
        if CHECK_TASK_MOM:
            self.pipeline_test_tools.stop_listen_mq()

    def test_upload_task(self):
        self._common_run(self._test_upload_task, "Error: can not do upload task.")
        notification_console("Info: the interface test is successful, please go to the bio-pass, zlims-pro page to check whether the sample is normally generated.")

    def _test_write_fastq_task(self):
        self.pipeline_test_tools.test_write_fastq_task()

    def test_write_fastq_task(self):
        self._common_run(self._test_write_fastq_task, "Error: can not do write fastq task.")

    def _test_analysis_task_for_bio_pass(self):
        self.pipeline_test_tools.test_analysis_task_for_bio_pass()
        if CHECK_TASK_MOM:
            self.pipeline_test_tools.stop_listen_mq()

    def test_analysis_task_for_bio_pass(self):
        self._common_run(self._test_analysis_task_for_bio_pass, "Error: can not do analysis task.")

    def _test_analysis_task(self):
        self.pipeline_test_tools.test_analysis_task()

    def test_analysis_task(self):
        self._common_run(self._test_analysis_task, "Error: can not do analysis task.")


class WholeTestRunner(BSTestRunner):

    def getReportAttributes(self, result):
        report_attrs = super(WholeTestRunner, self).getReportAttributes(result)
        ### 获取控制软件版本信息
        flag = False
        for item in result.result:
            for i in item:
                if isinstance(i, PipelineTest):
                    if hasattr(i, 'pipeline_test_tools') and hasattr(i.pipeline_test_tools, 'need_check_values'):
                        if len(i.pipeline_test_tools.warnings) > 0:
                            report_attrs.append(('Warning Messages',
                         '<span class="text text-warning"><strong>%s</strong></span>' % ';'.join(i.pipeline_test_tools.warnings)))
                        for k, v in i.pipeline_test_tools.need_check_values.items():
                            report_attrs.append((k, v))
                        flag = True
            if flag:
                break
        return report_attrs


def usage():
    VERSION = '0.0.1'
    DATE = '2020-04-14'

    ###### Usage
    USAGE = """

         Version %s  by zhouxianqiang@genomics.cn  %s

         Usage: python %s [ignore_analysis]
    """ % (VERSION, DATE, os.path.basename(sys.argv[0]))
    print(USAGE)


def suite(ignore_analysis=False, product="QC", sequencing_mode="PE"):
    global pipeline_test_tools
    global current_product
    current_product = product
    pipeline_test_tools = WholePipelineTest(product, sequencing_mode)
    test_suite = unittest.TestSuite()
    test_suite.addTest(PipelineTest("test_instrument_config"))
    test_suite.addTest(PipelineTest("test_mom_status"))
    test_suite.addTest(PipelineTest("test_create_dnb"))
    test_suite.addTest(PipelineTest("test_load_dnb_task"))
    test_suite.addTest(PipelineTest("test_sequencing_task"))
    if IS_T7:
        pass
        # test_suite.addTest(PipelineTest("test_write_fastq_task"))
        # if not ignore_analysis:
        #     test_suite.addTest(PipelineTest("test_analysis_task_for_bio_pass"))
    else:
        test_suite.addTest(PipelineTest("test_upload_task"))
#        if not ignore_analysis:
#            test_suite.addTest(PipelineTest("test_analysis_task"))
    return test_suite


def estimate_test_time(test_products, test_sequencing_modes):
    total_time = 0
    for product in test_products:
        time = get_analysis_time(product)
        total_time += time * len(test_sequencing_modes)
    m, s = divmod(total_time, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)


if __name__ == '__main__':
    global test_sample_number
    global IS_T7
    IS_T7 = False
    ignore_analysis = False
    if len(sys.argv) > 1:
        if sys.argv[1] == '-h':
            usage()
            sys.exit(0)
        if sys.argv[1] != 'ignore_analysis' and sys.argv[1] != 'test_t7':
            usage()
            sys.exit(0)
        elif sys.argv[1] == 'test_t7':
            IS_T7 = True
        else:
            ignore_analysis = True
    test_products = ['QC'] if ignore_analysis else TEST_PRODUCTS
    test_sequencing_modes = ['PE'] if ignore_analysis else TEST_SEQUENCING_MODES
    total_time = estimate_test_time(TEST_PRODUCTS, TEST_SEQUENCING_MODES)
    if ignore_analysis:
        total_time = "00:01:00"
    notification_console("============================")
    notification_console("Estimate time: %s" % total_time)
    notification_console("============================")
    for product in test_products:
        test_sample_number = TEST_SAMPLE_NUMBER
        if product in ONLY_SUPPORT_MORE_SAMPLE_PRODUCTS:
            test_sample_number = 2
            if TEST_SAMPLE_NUMBER > 2:
                test_sample_number = TEST_SAMPLE_NUMBER
        new_sequencing_modes = test_sequencing_modes
        if product in ONLY_SUPPORT_SE_PRODUCTS:
            new_sequencing_modes = ["SE"]
        if product in ONLY_SUPPORT_PE_PRODUCTS:
            new_sequencing_modes = ["PE"]
        for sequencing_mode in new_sequencing_modes:
            test_suite = suite(ignore_analysis, product, sequencing_mode)
            if ignore_analysis:
                report_path = os.path.join(sys.path[0], 'The_Unit_Test_Report.html')
            else:
                report_path = os.path.join(sys.path[0], '%s_%s_Unit_Test_Report.html' % (product, sequencing_mode))

            if os.path.exists(report_path):
                os.remove(report_path)
            with open(report_path, 'wb') as fh:
                runner = WholeTestRunner(
                            stream=fh,
                            title='Whole Pipeline Unit Test',
                            description=''
                            )

                # Use an external stylesheet.
                # See the Template_mixin class for more customizable options
                runner.STYLESHEET_TMPL = '<link rel="stylesheet" href="my_stylesheet.css" type="text/css">'

                # run the test
                notification_console(".")
                notification_console("Start test...")
                notification_console("Test Product: %s, Test sequencing mode: %s" % (product, sequencing_mode))
                notification_console("After the test is completed, you can see the detailed results in the test report: %s" % report_path)
                runner.run(test_suite)
                PipelineTest.last_test_status = True
