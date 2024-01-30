# coding: utf-8

import logging
import threading
import time

import perfdog_pb2
from perfdog import Test, TestSysProcessBuilder
from test_base import create_service, get_all_types, set_floating_window


def get_windows_device(service):
    for device in service.get_devices():
        if device.os_type() == perfdog_pb2.WINDOWS:
            return device
    return None


def main():
    # Log output configuration, you can configure it yourself if you have special needs
    # 日志输出配置，如果有特别的需要可自行配置
    logging.basicConfig(format="%(asctime)s-%(levelname)s: %(message)s", level=logging.INFO)

    # Create service object proxy
    # 创建服务对象代理
    service = create_service()

    # Get the device object
    # 获取设备对象
    device = get_windows_device(service)
    if device is None:
        logging.error("non-exist device")
        return

    # TODO:
    # Fill in the correct process PID and the dx version used by the test target process for rendering
    # You can use cmds.py in the same directory to get the current process list of Windows
    # You can fill in the type parameter according to your own needs to enable a list of performance indicator parameters. When the type value is None, use the indicator options that are enabled on the current device
    # To enable indicators, please refer to "Indicator parameter mapping table: https://perfdog.wetest.net/article_detail?id=176&issue_id=0&plat_id=2"
    # If you need to start collecting performance data for multiple devices in a single script process, you can run the run_test function multiple times in parallel through multi-threading
    # 填入正确进程PID以及测试目标进程渲染使用的dx版本
    # 可以使用同目录下cmds.py获取Windows当前的进程列表
    # 可以根据自己需要填写types参数，来启用的性能指标参数列表，types值为None时，使用当前设备已经开启的指标选项
    # 指标启用可以参考"指标参数映射表：https://perfdog.qq.com/article_detail?id=10210&issue_id=0&plat_id=2"
    # 如果单一脚本进程中需要启动针对多个设备性能数据收集，可以通过多线程的方式，并行运行多次run_test函数
    pid = 30120
    dx_version = perfdog_pb2.AUTO
    run_test(device, pid=pid, dx_version=dx_version,
             types=[perfdog_pb2.FPS, perfdog_pb2.FRAME_TIME, perfdog_pb2.WINDOWS_CPU, perfdog_pb2.WINDOWS_MEMORY],
             )


def run_test(device, pid, dx_version, types=None, dynamic_types=None, enable_all_types=False):
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

    # Automate general configuration to hide floating windows
    # 自动化一般配置隐藏浮窗
    set_floating_window(device)

    # Create the target App to be tested
    # 创建要测试目标App
    builder = test.create_test_target_builder(TestSysProcessBuilder)
    builder.set_pid(pid)
    builder.set_dx_version(dx_version)
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
