# Paaz 全流程启动分析测试工具


## T7模拟API测试步骤
- 将代码放到paaz服务器上，进入到whole_unit_test目录，打开config.py 配置相应配置项
- 在whole_unit_test目录下，执行 sh run_test.sh，等待测试完成
- 查看目录下生成的测试报告

## 个人电脑模拟测试步骤
- 进入到whole_unit_test目录，打开config.py 配置相应配置项
- 再进入whole_unit_test/mypackages目录，双击prepare_G50.bat或者prepare_G400.bat（将电脑模拟成测序仪，首次连接lims需要执行此步骤）
- 在whole_unit_test目录下，双击 run_test.bat，等待测试完成
- 打开目录下生成的测试报告，查看测试结果

## 测序仪上模拟API测试步骤
- 进入到whole_unit_test目录，打开config.py 配置相应配置项
- 在whole_unit_test目录下，双击 run_test.bat，等待测试完成
- 打开目录下生成的测试报告，查看测试结果

## 新增生信产品，如何添加到测试工具
- 进入到whole_unit_test目录，打开config.py，在TEST_PRODUCTS中添加产品编号
- 准备测试fastq，进入到whole_unit_test/test_fastq目录,创建对应产品编号的文件夹，并放置测试fastq文件，文件命名规范为（read1.fq.gz, read2.fq.gz 如果只支持SE的分析，只放read1.fq.gz即可，如果需要多组测试数据，则新增组的测试数据命名为read1.fq.gz__1, read1.fq.gz__2）
- 在下载zlims-pro中下载excel模板，只保留DNB SAMPLE Entry一个表，填写一条测试数据。并以如下命名保存模板文件 zlims_sample_excel\${language}\Sample_import_template${product}2020-05-18.xlsx（${language}代表语言，中英文各一份。${product}代表产品编号）