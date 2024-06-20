# coding: utf-8

import logging
import threading
import time

import perfdog_pb2
from perfdog import Test, TestSysProcessBuilder, TestAppBuilder
from test_base import create_service, get_all_types


def main():
    # Log output configuration, you can configure it yourself if you have special needs
    # 日志输出配置，如果有特别的需要可自行配置
    logging.basicConfig(format="%(asctime)s-%(levelname)s: %(message)s", level=logging.INFO)

    # Create service object proxy
    # 创建服务对象代理
    service = create_service()

    # TODO:
    # Add console device, mostly used for adding devices for the first time
    # 添加主机设备，多用于第一次添加设备
    service.add_remote_play_station_device(ip_address="192.168.0.0")
    service.add_remote_xbox_device(ip_address="192.168.0.0", password="test")
    time.sleep(2)

    # TODO:
    # Fill in the correct device ID
    # You can use cmds.py in the same directory to obtain the list of devices connected to the computer
    # 填入正确的设备ID
    # 可以使用同目录下cmds.py获取已连接到电脑的设备列表
    device = service.get_wifi_device('-')
    if device is None:
        logging.error("non-exist device")
        return

    # Check if the device is occupied
    # 确认设备是否被占用
    other_user = device.occupied_by_other_user()
    if not other_user:
        logging.info("device occupied by %s", other_user)

    # TODO:
    # Continuing will force the device to connect
    # Fill the package name of the test app
    # You can use cmds.py in the same directory to obtain the App list of the corresponding devices
    # 继续执行会强行连接设备
    # 填入测试app的包名
    # 可以使用同目录下cmds.py获取相应设备的App列表
    run_test(device=device, package_name='-', types=[perfdog_pb2.FPS, perfdog_pb2.FRAME_TIME])


def run_test(device, package_name, types=None, dynamic_types=None, enable_all_types=False):
    # Create test object
    # 创建测试对象
    test = Test(device)

    # Set up performance data callback
    # 设置有性能数据回调
    evt = threading.Event()
    test.set_first_perf_data_callback(lambda: evt.set())

    # Output performance data, it is recommended to enable it during debugging
    # 输出性能数据，调试过程中建议开启
    test.set_perf_data_callback(lambda perf_data: logging.info(perf_data))

    # Output the alarm and error information during the test. It is recommended to keep it. It is easy to check the log if there is a problem
    # 输出测试过程中告警和错误信息，建议保留，出问题便于查日志
    test.set_error_perf_data_callback(lambda perf_data: logging.info("PerfDog: %s", perf_data.errorData.msg))
    test.set_warning_perf_data_callback(lambda perf_data: logging.warning("PerfDog: %s", perf_data.warningData.msg))

    # Create the target App to be tested. PS5 supports creating the target process to be tested.
    # 创建要测试目标App，PS5支持创建要测试目标进程
    builder = test.create_test_target_builder(TestAppBuilder)
    builder.set_package_name(package_name)
    # builder = test.create_test_target_builder(TestSysProcessBuilder)
    # builder.set_pid(pid)
    test.set_test_target(builder.build())

    # Enable and disable related performance indicator types
    # 启用和禁用相关性能指标类型
    if enable_all_types:
        types, dynamic_types = get_all_types(device)

    if types is not None:
        test.set_types(*types)

    if dynamic_types is not None:
        test.set_dynamic_types(*dynamic_types)

    try:
        # Start performance data collection
        # 启动性能数据采集
        test.start()

        # Wait for performance data
        # Need to use set_first_perf_data_callback to enable
        # 等待有性能数据
        # 需要使用set_first_perf_data_callback来启用
        evt.wait()

        # TODO:
        # It is recommended to add automated test processing logic here
        # 建议在此处添加自动化测试处理逻辑
        time.sleep(10)
        test.set_label('label_x')
        time.sleep(2)
        test.add_note('n1', 12 * 1000)
        time.sleep(2)
        test.stop()
        test.save_data()

    finally:
        # Release necessary resources
        # 必要的资源释放
        if test.is_start():
            test.stop()


if __name__ == '__main__':
    main()
