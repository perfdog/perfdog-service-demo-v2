# coding: utf-8

import logging
import threading
import time

import perfdog_pb2
from perfdog import Test, TestAppBuilder
from test_base import create_service, get_all_types, set_floating_window


def main():
    # Log output configuration, you can configure it yourself if you have special needs
    # 日志输出配置，如果有特别的需要可自行配置
    logging.basicConfig(format="%(asctime)s-%(levelname)s: %(message)s", level=logging.INFO)

    # Create service object proxy
    # 创建服务对象代理
    service = create_service()

    # Configure whether to install floating window App, valid for Android devices
    # If the App has been installed on the device to be tested, please uninstall it from the device manually before continuing to use it
    # Enable one of the following two configurations according to your own testing requirements
    # Enable installation
    # service.enable_install_apk()
    # Disable installation. You can set it not to install PerfDog APK to reduce unnecessary pauses and interruptions when running automation
    # 配置是否安装浮窗App，针对安卓设备有效
    # 如果App已经安装到要测试的设备上，请先手工从设备卸载之后继续使用
    # 按照自己的测试要求启用下面两个配置中的一个
    # 启用安装
    # service.enable_install_apk()
    # 禁止安装,可设置不安装PerfDog APK，跑自动化时减少不必要的暂停打断
    service.disable_install_apk()

    # TODO:
    # Fill in the correct device ID and the package name of the test app
    # You can use cmds.py in the same directory to obtain the list of devices connected to the computer and the App list of the corresponding devices
    # You can fill in the type parameter according to your own needs to enable a list of performance indicator parameters. When the type value is None, use the indicator options that are enabled on the current device
    # To enable indicators, please refer to "Indicator parameter mapping table: https://perfdog.wetest.net/article_detail?id=176&issue_id=0&plat_id=2"
    # If you need to start collecting performance data for multiple devices in a single script process, you can run the run_test_app function multiple times in parallel through multi-threading
    # 填入正确的设备ID，填入测试app的包名
    # 可以使用同目录下cmds.py获取已连接到电脑的设备列表及相应设备的App列表
    # 可以根据自己需要填写types参数，来启用的性能指标参数列表，types值为None时，使用当前设备已经开启的指标选项
    # 指标启用可以参考"指标参数映射表：https://perfdog.qq.com/article_detail?id=10210&issue_id=0&plat_id=2"
    # 如果单一脚本进程中需要启动针对多个设备性能数据收集，可以通过多线程的方式，并行运行多次run_test_app函数

    device = service.get_usb_device('-')
    if device is None:
        logging.error("device not found")
        return

    run_test_app(device,
                 package_name='-',
                 types=[perfdog_pb2.FPS, perfdog_pb2.FRAME_TIME, perfdog_pb2.CPU_USAGE, perfdog_pb2.MEMORY],
                 dynamic_types=[
                     (perfdog_pb2.GPU_COUNTER, 'GPU General'),
                     (perfdog_pb2.GPU_COUNTER, 'GPU Stalls'),
                 ],
                 )


def run_test_app(device, package_name, types=None, dynamic_types=None, enable_all_types=False):
    # Create test object
    # 创建测试对象
    test = Test(device)

    # Set the memory indicator sampling frequency in seconds, valid for Android devices
    # Generally no setting is required, just use the default value
    # 设置内存指标采样频率，单位秒，安卓设备有效
    # 一般无需设置，使用缺省值即可
    # device.set_memory_sampling_frequency(4)

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
    builder = test.create_test_target_builder(TestAppBuilder)
    builder.set_package_name(package_name)
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
