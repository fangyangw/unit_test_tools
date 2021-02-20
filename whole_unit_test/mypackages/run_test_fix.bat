python -m pip install --no-index --find-links=mypackages -r requirements.txt
python test_for_whole_pipeline.py
@ECHO ...
@ECHO Test Complete, Please check the test report in the directory.
timeout /T 5