## Language
- [English](readme.md)
- [中文](readme_zh.md)

## perfdog-service-demo-v2
+ This demo helps students who want to quickly get started building performance automation.

## Project usage conditions
1. Install python3, just download it from the official website, python3.10 is recommended
2. Install the python3 library, grpcio (1.48.2) and protobuf (4.25.1). It is recommended to use pip to install;

## File directory description
```bash
perfdog-service-demo-v2
├── cmds.py
├── config.py
├── perfdog.py
├── perfdog_pb2.py
├── perfdog_pb2_grpc.py
├── perfdog_references.py
├── readme_zh.md
├── test.py
├── test_windows.py
├── test_network.py
└── test_console.py
```
- test.py、test_windows.py、test_console.py collect performance data script template, test_network.py simulates network scenarios, which can be modified on this basis
- cmds.py Get device list and app list
- perfdog_references.py sample code

## Steps for usage
1. [Apply for token](https://perfdog.wetest.net/article_detail?id=156&issue_id=0&plat_id=2)
2. [Download software](https://perfdog.wetest.net/perfdogservice)
3. Configure config.py
```python
# Configure the Service path and the applied token
SERVICE_TOKEN = '-'
SERVICE_PATH = '-'
```
4. Use command line tools to quickly obtain device application information:
```python
# Get device list
python cmds.py getdevices
# Get App list
python cmds.py getapps device_id
# Get the current system process list
python cmds.py getsysprocesses device_id
# Get the performance indicators supported by the current device
python cmds.py gettypes device_id
# Get the current user's default and saved network templates
python cmds.py getpresetnetworktemplate
# Stop PerfDogService
python cmds.py killserver
```

> If you need to test a Windows or Xbox application later, execute the above command in a terminal started in administrator mode.

5. Configure test parameters
+ Mobile device performance testing
```python
# Fill in the correct device ID and the package name of the test app
# You can use cmds.py in the same directory to obtain the list of devices connected to the computer, the App list of the corresponding devices, and the supported performance indicators.
# You can fill in the type and dynamic_types parameters according to your own needs to enable the performance indicator parameter list
# To enable indicators, please refer to "Indicator parameter mapping table: https://perfdog.wetest.net/article_detail?id=176&issue_id=0&plat_id=2"
# If you need to start collecting performance data for multiple devices in a single script process, you can run the run_test_app function multiple times in parallel through multi-threading.
device = service.get_usb_device('-')
run_test_app(device,
              package_name='-',
              types=[perfdog_pb2.FPS, perfdog_pb2.FRAME_TIME, perfdog_pb2.CPU_USAGE, perfdog_pb2.MEMORY],
              dynamic_types=[
                  (perfdog_pb2.GPU_COUNTER, 'GPU General'),
                  (perfdog_pb2.GPU_COUNTER, 'GPU Stalls'),
             ])
```

> See test.py script sample
>

+ PC performance test
```python
# Fill in the correct process PID and the dx version used by the test target process for rendering
# You can use cmds.py in the same directory to get the current process list of Windows
# You can fill in the type parameter according to your own needs to enable a list of performance indicator parameters. When the type value is None, use the indicator options that are enabled on the current device.
# To enable indicators, please refer to "Indicator parameter mapping table: https://perfdog.wetest.net/article_detail?id=176&issue_id=0&plat_id=2"
# If you need to start collecting performance data for multiple devices in a single script process, you can run the run_test function multiple times in parallel through multi-threading.
pid=30876
dx_version = perfdog_pb2.AUTO
run_test(device, pid=pid, dx_version=dx_version,
             types=[perfdog_pb2.FPS, perfdog_pb2.FRAME_TIME, perfdog_pb2.WINDOWS_CPU, perfdog_pb2.WINDOWS_MEMORY],
             enable_all_types=True,
             )
```

> See test_windows.py script sample
>

+ network test
```python
# Fill in the correct device ID and the package name of the test app
# You can use cmds.py in the same directory to obtain the list of devices connected to the computer, the App list of the corresponding devices, presets and saved network templates
# User-defined templates can refer to the create_customized_template() method in the script. For indicator meanings, please refer to https://perfdog.wetest.net/article_detail?id=145&issue_id=0&plat_id=1
# Fill in the network template list of the test process
# If you need to start network testing for multiple devices in a single script process, you can run the run_test_app function multiple times in parallel through multi-threading.
device = service.get_usb_device('-')
templates = create_templates()
run_test_app(device, package_name='-', templates=tempates)
```

> See test_network.py script sample
>

+ PlayStation5 & Xbox performance test
```python
# Add console device, mostly used for adding devices for the first time
# Fill in the correct device ID and the package name of the test app
# You can use cmds.py in the same directory to obtain the list of devices connected to the computer, the App list of the corresponding devices, and the supported performance indicators
# You can fill in the type parameter according to your own needs to enable a list of performance indicator parameters. When the type value is None, use the indicator options that are enabled on the current device
# If you need to start collecting performance data for multiple devices in a single script process, you can run the run_test function multiple times in parallel through multi-threading.
service.add_remote_play_station_device(ip_address="192.168.0.0")
service.add_remote_xbox_device(ip_address="192.168.0.0", password="test")
device = service.get_wifi_device('-')
run_test(device, package_name='-', types=[perfdog_pb2.FPS, perfdog_pb2.FRAME_TIME])
```

> See test_console.py script sample

6. Modify and run test.py or test_windows.py or test_network.py or test_console.py
+ You can enable/use related performance indicator types according to your own needs, and you can also enable your own automated testing logic in this script.

> test_windows.py test windows application and test_console.py test xbox application need to be started as administrator
>

## Precautions
If you no longer need to collect data, you must stop the test, which will affect billing. The service supports automatic collection of data in the background, even if the script is not running; you can use the cmds.py script to stop the running of the service, so you don't have to worry about billing issues.