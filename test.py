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

    # TODO:
    # 填入正确的设备ID，填入测试app的包名
    # 可以使用同目录下cmds.py获取已连接到电脑的设备列表及相应设备的App列表
    # 可以根据自己测试目的，启用、禁用相应的指标类型
    # 如果单一脚本进程中需要启动针对多个设备性能数据收集，可以通过多线程的方式，并行运行多次run_test_app函数

    device = service.get_usb_device('-')
    run_test_app(device,
                 package_name='-',
                 enable_types=[perfdog_pb2.WAKEUP],
                 disable_types=[perfdog_pb2.IOS_GPU_USAGE, perfdog_pb2.SYSTEM_LOG])


def run_test_app(device, package_name, enable_types=None, disable_types=None):
    # 创建测试对象
    test = Test(device)

    # 设置有性能数据回调和性能数据回调处理函数
    # 不需要的话，这两个回调可以不设置
    evt = threading.Event()
    test.set_first_perf_data_callback(lambda: evt.set())
    test.set_perf_data_callback(lambda perf_data: logging.info(perf_data))

    # 创建要测试目标App
    builder = test.create_test_target_builder(TestAppBuilder)
    builder.set_package_name(package_name)
    test.set_test_target(builder.build())

    # 启用和禁用相关性能指标类型
    if enable_types is not None:
        test.enable_types(*enable_types)

    if disable_types is not None:
        test.disable_types(*disable_types)

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


if __name__ == '__main__':
    main()
