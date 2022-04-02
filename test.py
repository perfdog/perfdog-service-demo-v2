# coding: utf-8

import logging
import time
import threading
from perfdog import Service, Test, TestAppBuilder, TestSysProcessBuilder
import perfdog_pb2
from config import SERVICE_TOKEN, SERVICE_PATH


def main():
    # 日志输出配置，如果有特别的需要可自行配置
    logging.basicConfig(format="%(asctime)s-%(levelname)s: %(message)s", level=logging.INFO)

    # 创建服务对象代理
    service = Service(SERVICE_TOKEN, SERVICE_PATH)

    # 配置是否安装浮窗App，针对安卓设备有效
    # 如果App已经安装到要测试的设备上，请先手工从设备卸载之后继续使用
    # 按照自己的测试要求启用下面两个配置中的一个
    # 禁止安装,可设置不安装PerfDog APK，跑自定化时减少不必要的暂停打断
    # service.disable_install_apk()
    # 启用安装
    # service.enable_install_apk()

    # TODO:
    # 填入正确的设备ID，填入测试app的包名
    # 可以使用同目录下cmds.py获取已连接到电脑的设备列表及相应设备的App列表
    # 可以根据自己需要填写types参数，来启用的性能指标参数列表，types值为None时，使用当前设备已经开启的指标选项
    # 如果单一脚本进程中需要启动针对多个设备性能数据收集，可以通过多线程的方式，并行运行多次run_test_app函数

    device = service.get_usb_device('-')
    run_test_app(device,
                 package_name='-',
                 types=[perfdog_pb2.FPS, perfdog_pb2.FRAME_TIME, perfdog_pb2.CPU_USAGE, perfdog_pb2.MEMORY])


def print_perf_data(perf_data):
    if perf_data.HasField('warningData'):
        msg = perf_data.warningData.msg
        logging.warning(msg)
    elif perf_data.HasField('errorData'):
        msg = perf_data.errorData.msg
        logging.error(msg)
    else:
        logging.info(perf_data)


def run_test_app(device, package_name, types=None, enable_types=None, disable_types=None):
    # 创建测试对象
    test = Test(device)

    # 设置有性能数据回调和性能数据回调处理函数
    # 不需要的话，这两个回调可以不设置
    evt = threading.Event()
    test.set_first_perf_data_callback(lambda: evt.set())
    test.set_perf_data_callback(print_perf_data)

    # 创建要测试目标App
    builder = test.create_test_target_builder(TestAppBuilder)
    builder.set_package_name(package_name)
    test.set_test_target(builder.build())

    # 启用和禁用相关性能指标类型
    if types is not None:
        test.set_types(*types)

    if enable_types is not None:
        test.enable_types(*enable_types)

    if disable_types is not None:
        test.disable_types(*disable_types)

    try:
        # 启动性能数据采集
        test.start()

        # 等待有性能数据
        # 需要使用set_first_perf_data_callback来启用
        evt.wait()

        # TODO:
        # 建议在此处添加自动化测试处理逻辑
        time.sleep(10)
        test.set_label('label_x')
        time.sleep(2)
        test.add_note('n1', 12 * 1000)
        time.sleep(2)
        test.stop()
        test.save_data()

    finally:
        # 必要的资源释放
        if test.is_start():
            test.stop()


if __name__ == '__main__':
    main()
