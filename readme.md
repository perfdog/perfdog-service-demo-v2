
# perfdog-service-demo-v2
+ 该Demo帮助有诉求的同学快速上手搭建性能自动化。

## 项目使用条件
1. 安装python3，从官网下载最新python3版本即可；
2. 安装python3库，grpcio(1.43.0)和protobuf(3.17.3)，推荐使用pip安装；

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
4. 使用命令行工具快速获取设备应用信息：
```python
# 获取设备列表
python cmds.py getdevices
# 获取App列表
python cmds.py getapps device_id
# 获取当前系统进程列表
python cmds.py getsysprocesses device_id
# 获取当前设备支持获取的性能指标
python cmds.py gettypes device_id
# 停止PerfDogService
python cmds.py killserver
```

> 如果后续需要测试的是windows应用，上面命令的执行在管理员方式启动的终端中执行

5. 配置测试参数
+ 移动设备性能测试
```python
# 填入正确的设备ID，填入测试app的包名
# 可以使用同目录下cmds.py获取已连接到电脑的设备列表、相应设备的App列表和支持的性能指标
# 可以根据自己需要填写types和dynamic_types参数，来启用的性能指标参数列表
# 指标启用可以参考"指标参数映射表：https://perfdog.qq.com/article_detail?id=10210&issue_id=0&plat_id=2"
# 如果单一脚本进程中需要启动针对多个设备性能数据收集，可以通过多线程的方式，并行运行多次run_test_app函数
device = service.get_usb_device('-')
run_test_app(device,
             package_name='-',
             types=[perfdog_pb2.FPS, perfdog_pb2.FRAME_TIME, perfdog_pb2.CPU_USAGE, perfdog_pb2.MEMORY],
             dynamic_types=[
                 (perfdog_pb2.GPU_COUNTER, 'GPU General'),
                 (perfdog_pb2.GPU_COUNTER, 'GPU Stalls'),
            ])
```

> 参见test.py脚本样例
> 

+ PC性能测试
```python
# 填入正确进程PID以及测试目标进程渲染使用的dx版本
# 可以使用同目录下cmds.py获取Windows当前的进程列表
# 可以根据自己需要填写types参数，来启用的性能指标参数列表，types值为None时，使用当前设备已经开启的指标选项
# 指标启用可以参考"指标参数映射表：https://perfdog.qq.com/article_detail?id=10210&issue_id=0&plat_id=2"
# 如果单一脚本进程中需要启动针对多个设备性能数据收集，可以通过多线程的方式，并行运行多次run_test函数
pid = 30876
dx_version = perfdog_pb2.AUTO
run_test(device, pid=pid, dx_version=dx_version,
            types=[perfdog_pb2.FPS, perfdog_pb2.FRAME_TIME, perfdog_pb2.WINDOWS_CPU, perfdog_pb2.WINDOWS_MEMORY],
            enable_all_types=True,
            )
```

> 参见test_windows.py脚本样例
> 


6. 修改运行test.py 或者 test_windows.py
+ 可以根据自己需要启用/用相关性能指标类型，同时也可在此脚本中启用自己的自动化测试逻辑

> test_windows.py测试windows应用需要以管理员方式启动

## 注意事项
如果不需要收集数据了，一定要停止测试，会影响计费，service是支持后台自动收集数据的，即便脚本不运行了；可以使用cmds.py脚本停止service的运行，就不用担心计费的问题了；
