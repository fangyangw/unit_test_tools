Whole pipeline unit test(V1.0)
=======================================

## 声明

- 此项测试只做全流程API验证，不对各软件功能组件功能做详细验证

### 测试的前提条件

- 已经完成测序仪QC并且不再变更ISW和ZebraCall软件版本；
- 配置测序仪ISW软件配置参数使ISW软件连接上ZLIMS；
- 配置分析服务器连接上ZLIMS；
- ZLIMS上配置好rsync。

### 配置测试应用类型
- 获取此项测试数据包，拷贝到测序仪系统C盘根目录下；
- 使用文本编辑器打开whole_unit_test文件夹下的"config.py" 文件,根据实际需求修改配置；
- 具体需要修改的配置如：ZLIMS_HOSTNAME（修改为ZLIMS服务器ip地址），TEST_PRODUCTS（对需要测试的产品类型取消注释#，
支持多产品同时测试），TEST_LANGUAGE（修改为当前部署的ZLIMS语言版本，有en、cn两个版本）；
- 保存以上修改项。
- T7测试可能需要修改WRITE_FASTQ_WDL_PATH（修改为write fastq wdl的安装路径, 如果flag目录有修改请修改write fastq wdl文件中flag_dir的值）

### 运行测试批处理文件
- 确认ISW和ZebraCall后台服务处在运行状态，并进入到ISW用户界面，处于录入DNB ID界面；
- 测试全流程：双击 "run_test.bat" 文件（不可以以管理员身份运行），等待运行结束；
- T7测试全流程，在ZLIMS服务器上运行：sh run_test.sh，等待运行结果；
- 测试样本编号为sample_unit_test_*，api测试跑完需要在ZLIMS Pro页面确认分析报告是否生成

### 查看测试报告
- 测试结束后会在当前目录生成对应的测试报告，点击查看即可。

### 测试结果判定
- 报告中的所有的测试用例必须全部通过。

### 保留测试报告
- 测试结束后可以拷贝测试报告，做内部交付确认等其他用途。
