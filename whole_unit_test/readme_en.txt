Whole pipeline unit test(V1.0)
=======================================
## Statement

- This test only performs full-process API verification, and does not perform detailed verification on the function of each software functional component

### Prerequisites for testing

- The sequencer QC has been completed and the ISW and ZebraCall software versions will not be changed;
- Configure the sequencer ISW software configuration parameters to connect the ISW software to ZLIMS;
- Configure the analysis server to connect to ZLIMS;
- Configure rsync on ZLIMS.

### Configure test application type
- Obtain this test data package and copy it to the root directory of the C drive of the sequencer system;
- Use a text editor to open the "config.py" file in the whole_unit_test folder and modify the configuration according to actual needs;
- The specific configuration that needs to be modified is: ZLIMS_HOSTNAME (modified to the IP address of the ZLIMS server),
TEST_PRODUCTS (uncomment # for the product type to be tested#, Support simultaneous testing of multiple products)，
TEST_LANGUAGE (modified to the currently deployed ZLIMS language version, there are two versions of en and cn);
- T7 test may need to modify WRITE_FASTQ_WDL_PATH (modified to the installation path of write fastq wdl,
if the flag directory is modified, please modify the value of flag_dir in write fastq wdl file)
- Save the above modifications.

### Run test batch file
- Confirm that the ISW and ZebraCall background services are running, and enter the ISW user interface, which is in the input DNB ID interface;
- The whole process of testing: double-click the "run_test.bat" file (it cannot be run as an administrator) and wait for the end of the run;
- The whole process of T7 test, run on the ZLIMS server: sh run_test.sh, wait for the running result;
- The test sample number is sample_unit_test_*, you need to confirm whether the analysis report is generated on the ZLIMS Pro page after running the api test

### View test report
- After the test, the corresponding test report will be generated in the current directory, click to view.

### Test result judgment
- All test cases in the report must pass.

### Keep test report
- After the test, you can copy the test report for other purposes such as internal delivery confirmation.