from mypackages.tools import WholePipelineTest
from config import TEST_PRODUCTS, TEST_SEQUENCING_MODES, CHECK_TASK_MOM
import threading
import time

if __name__ == '__main__':
    # pipeline_test_tools = WholePipelineTest(TEST_PRODUCTS[0])
    # pipeline_test_tools.check_dca_status()
    # pipeline_test_tools.get_machine_id()
    # pipeline_test_tools.check_machine_config()
    # pipeline_test_tools.create_samples(2)
    # pipeline_test_tools.create_library_task()
    # pipeline_test_tools.create_pool_task()
    # pipeline_test_tools.create_make_dnb_task()
    # pipeline_test_tools.create_load_dnb_task()
    # pipeline_test_tools.create_sequencing_task()
    # pipeline_test_tools.create_upload_task()
    # pipeline_test_tools.test_analysis_task()

    ####  test for halos
    product = TEST_PRODUCTS[0]
    product = "WES"
    # dnb_sn = "%s_dnb_117_06" % (product.lower().split('_')[-1])
    dnb_sn = "wes_test_dnb_002"

    pipeline_test_tools = WholePipelineTest(product, "PE")
    pipeline_test_tools.get_machine_id()
    pipeline_test_tools.check_machine_config()
    pipeline_test_tools.check_mom_service_status()

    pipeline_test_tools1 = WholePipelineTest(product, "PE")
    pipeline_test_tools1.get_machine_id()
    pipeline_test_tools1.check_machine_config()
    # pipeline_test_tools.delete_dnb()
    # pipeline_test_tools.create_dnb()
    if CHECK_TASK_MOM:
        pipeline_test_tools.start_listen_mq()
    t1 = threading.Thread(target=pipeline_test_tools1.create_load_dnb_task, args=(dnb_sn,))
    t2 = threading.Thread(target=pipeline_test_tools.create_load_dnb_task, args=(dnb_sn,))
    # pipeline_test_tools1.create_load_dnb_task(dnb_sn)
    # pipeline_test_tools.create_load_dnb_task(dnb_sn)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    pipeline_test_tools1.create_sequencing_task()
    pipeline_test_tools1.create_upload_task()
    print("first dnb have finish.")
    time.sleep(5)
    pipeline_test_tools.create_sequencing_task()
    pipeline_test_tools.create_upload_task()
    if CHECK_TASK_MOM:
        pipeline_test_tools.stop_listen_mq()

