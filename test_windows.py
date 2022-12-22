# coding: utf-8

import logging
import time
import threading
from perfdog import Service, Test, TestTarget
import perfdog_pb2
from config import SERVICE_TOKEN, SERVICE_PATH


def get_windows_device(service):
    for device in service.get_devices():
        if device.os_type() == perfdog_pb2.WINDOWS:
            return device
    return None


def get_sys_process(device, pid):
    for process in device.get_sys_processes():
        if process.pid == pid:
            return process
    return None


def create_test_target(device, pid, dx_version):
    sys_process = get_sys_process(device, pid)
    return TestTarget(False, perfdog_pb2.StartTestSysProcessReq(device=device.real_device(),
                                                                sysProcessInfo=sys_process,
                                                                hideFloatingWindow=True,
                                                                dxVersion=dx_version))


def set_floating_window(device):
    position = perfdog_pb2.HIDE
    font_color = perfdog_pb2.Color(red=1.0, green=1.0, blue=0.0, alpha=1.0)
    record_hotkey = ''
    add_label_hotkey = ''
    device.set_floating_window_preferences(position, font_color, record_hotkey, add_label_hotkey)


def main():
    # 日志输出配置，如果有特别的需要可自行配置
    logging.basicConfig(format="%(asctime)s-%(levelname)s: %(message)s", level=logging.INFO)

    # 创建服务对象代理
    service = Service(SERVICE_TOKEN, SERVICE_PATH)

    # 获取设备对象
    device = get_windows_device(service)

    # TODO:
    # 填入正确进程PID以及测试目标进程渲染使用的dx版本
    # 可以使用同目录下cmds.py获取Windows当前的进程列表
    # 可以根据自己需要填写types参数，来启用的性能指标参数列表，types值为None时，使用当前设备已经开启的指标选项
    # 指标启用可以参考"指标参数映射表：https://perfdog.qq.com/article_detail?id=10210&issue_id=0&plat_id=2"
    # 如果单一脚本进程中需要启动针对多个设备性能数据收集，可以通过多线程的方式，并行运行多次run_test函数
    pid = 23836
    dx_version = perfdog_pb2.AUTO
    run_test(device, pid=pid, dx_version=dx_version,
             types=[perfdog_pb2.FPS, perfdog_pb2.FRAME_TIME, perfdog_pb2.WINDOWS_CPU, perfdog_pb2.WINDOWS_MEMORY]
             )


def print_perf_data(perf_data):
    if perf_data.HasField('warningData'):
        msg = perf_data.warningData.msg
        logging.warning(msg)
    elif perf_data.HasField('errorData'):
        msg = perf_data.errorData.msg
        logging.error(msg)
    else:
        logging.info(perf_data)


def get_all_types(device):
    types, dynamicTypes = device.get_available_types()
    return [ty for ty in types], [(dynamicType.type, dynamicType.category) for dynamicType in dynamicTypes]


def run_test(device, pid, dx_version, types=None, enable_all_types=False):
    # 创建测试对象
    test = Test(device)

    # 设置有性能数据回调和性能数据回调处理函数
    # 不需要的话，这两个回调可以不设置
    evt = threading.Event()
    test.set_first_perf_data_callback(lambda: evt.set())
    test.set_perf_data_callback(print_perf_data)

    # 自动化一般配置隐藏浮窗
    set_floating_window(device)

    # 设置测试目标
    test.set_test_target(create_test_target(device, pid, dx_version))

    # 启用和禁用相关性能指标类型
    if enable_all_types:
        types, dynamic_types = get_all_types(device)

    if types is not None:
        test.set_types(*types)

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
