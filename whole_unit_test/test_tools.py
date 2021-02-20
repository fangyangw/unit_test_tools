import sys
import os
sys.path.append(os.path.join("mypackages", "venv"))
from mypackages.tools import WholePipelineTest
from config import TEST_PRODUCTS, TEST_SEQUENCING_MODES, CHECK_TASK_MOM

if __name__ == '__main__':
    pipeline_test_tools = WholePipelineTest(TEST_PRODUCTS[0])
    pipeline_test_tools.import_dnb_sample_to_lims(1)
    #pipeline_test_tools.get_machine_id()
    #pipeline_test_tools.check_machine_config()
    #pipeline_test_tools.check_mom_service_status()
    #pipeline_test_tools.start_listen_mq()
    # dnb_id = "%s_dnb_unit_test_%s" %(TEST_PRODUCTS[0], current_test_id)
    # pipeline_test_tools.create_load_dnb_task(dnb_id)
    # pipeline_test_tools.create_sequencing_task()
    # pipeline_test_tools.test_write_fastq_task()
    # pipeline_test_tools.test_analysis_task_for_bio_pass()
    # pipeline_test_tools.stop_listen_mq()



    # pipeline_test_tools.create_upload_task()
    # pipeline_test_tools.test_analysis_task()

    # ####  test for halos
    # test_num = 4
    # for product in ["WGS"]: #TEST_PRODUCTS:
    #     pipeline_test_tools = WholePipelineTest(product, "PE")
    #     pipeline_test_tools.get_machine_id()
    #     pipeline_test_tools.check_machine_config()
    #     pipeline_test_tools.check_mom_service_status()
    #     # pipeline_test_tools.delete_dnb()
    #     # pipeline_test_tools.create_dnb()
    #     if CHECK_TASK_MOM:
    #         pipeline_test_tools.start_listen_mq()
    #     dnb_sn = "%s_1en_dnb_00%s" % (product.lower().split('_')[-1], test_num)
    #     pipeline_test_tools.create_load_dnb_task(dnb_sn)
    #     pipeline_test_tools.create_sequencing_task()
    #     # pipeline_test_tools.create_upload_task()
    #     if CHECK_TASK_MOM:
    #         pipeline_test_tools.stop_listen_mq()

