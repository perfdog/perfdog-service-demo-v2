
# perfdog-service-demo-v2 
+ 该Demo帮助有诉求的同学快速上手搭建性能自动化。

## 项目使用条件
1. 安装python3，从官网下载最新python3版本即可；
2. 安装python3库，grpcio(1.23.0)和protobuf(3.10.0)，推荐使用pip安装；

## 文件目录说明
```bash
perfdog-service-demo-v2  
├── cmds.py
├── config.py
├── perfdog.py
├── perfdog_pb2.py
├── perfdog_pb2_grpc.py
├── perfdog_references.py
├── readme.md
└── test.py
```
- test.py 收集性能数据脚本模板，可在此基础上修改
- cmds.py 获取设备列表和app列表
- perfdog_references.py 示例代码

## 使用步骤
1. [申请token](https://perfdog.qq.com/article_detail?id=10144&issue_id=0&plat_id=2)
2. [下载软件](https://perfdog.qq.com/perfdogservice)
3. 配置config.py
```python
# 配置Service路径和申请到的token
SERVICE_TOKEN = '-'
SERVICE_PATH = '-'
```
4. 使用命令行工具获取设备列表和app列表：
```bash
python cmds.py getdevices
python cmds.py getapps device_id
```
5. 将获取到的设备id和app的packageName更新到test.py中
```python
# 填入正确的设备ID，填入测试app的包名
# 可以使用同目录下cmds.py获取已连接到电脑的设备列表及相应设备的App列表
device = service.get_usb_device('-')
run_test_app(device,
             package_name='-',
             types=[perfdog_pb2.FPS, perfdog_pb2.FRAME_TIME, perfdog_pb2.CPU_USAGE, perfdog_pb2.MEMORY])
```
- types：需要启用的性能指标参数列表,值为None时，启用设备默认开启的性能指标
6. 修改运行test.py
+ 可以根据自己需要启用/用相关性能指标类型，同时也可在此脚本中启用自己的自动化测试逻辑
