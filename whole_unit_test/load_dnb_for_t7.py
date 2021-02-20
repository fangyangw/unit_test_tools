from mypackages.tools import WholePipelineTest
from config import TEST_PRODUCTS, TEST_SEQUENCING_MODES, CHECK_TASK_MOM

if __name__ == '__main__':
    pipeline_test_tools = WholePipelineTest(TEST_PRODUCTS[0])
    pipeline_test_tools.get_machine_id()
    # pipeline_test_tools.check_machine_config()
    pipeline_test_tools.check_mom_service_status()
    pipeline_test_tools.start_listen_mq()
    dnb_id = input("input DNB ID：")
    flowcell_id = input("input Flowcell ID：")
    aa = input("\nPlease make sure is correctly. DNB ID: %s,  Flowcell ID: %s\nPrint Enter to continue. Ctrl+C to break." %(dnb_id, flowcell_id))
    print("Starting load dnb.")
    pipeline_test_tools.create_load_dnb_task(dnb_id, flowcell_id)
    print("Load dnb................completed.")
    pipeline_test_tools.stop_listen_mq()
