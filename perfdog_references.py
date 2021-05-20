# coding: utf-8

import logging
import time
from perfdog import Service, Test, TestSysProcessBuilder
import perfdog_pb2


def run(service, device_id=None,
        upload_url=None,
        case_id=None,
        task_name=None,
        package_name=None):
    # 获取设备列表
    for device in service.get_devices():
        logging.info(device)

    # 监听设备连接、断开事件
    # stream = service.get_device_event_stream(lambda e: logging.info(e))
    # time.sleep(30)
    # stream.stop()

    # 配置第三方数据上传服务
    if upload_url is not None:
        service.set_global_data_upload_server(upload_url, perfdog_pb2.JSON)
        service.clear_global_data_upload_server()

    # 分享case, 过期时间单位为分钟
    if case_id is not None:
        logging.info("shareCase: %s", service.share_case(case_id, 8 * 24 * 60))

    # 创建任务
    # 归档case到任务
    if task_name is not None and case_id is not None:
        task_id = service.create_task(task_name)
        service.archive_case_to_task(task_id, case_id)

    # 针对设备的api接口验证
    device = service.get_usb_device(device_id)
    if device is not None:
        # 初始化设备
        device.init()

        # 获取设备信息
        logging.info('get_info: %s', device.get_info())

        # 获取设备状态
        logging.info('get_status: %s', device.get_status())

        # 获取设备app列表
        apps = device.get_apps()
        for app in apps:
            logging.info(app.packageName)

        # 查找app
        app = device.get_app(package_name)
        logging.info('get_app: %s', app)
        # logging.info('get_app_running_processes: %s', device.get_app_running_processes(app))
        # logging.info('get_app_windows_map: %s', device.get_app_windows_map(app))
        # logging.info('get_sys_processes: %s', device.get_sys_processes())

        # 设置截屏间隔
        # device.set_screenshot_interval(6)

    # 停止服务
    # service.kill_server()

    return


def run_test_sys_process(device, process_name):
    test = Test(device)
    builder = test.create_test_target_builder(TestSysProcessBuilder)
    builder.set_process_name(process_name)
    test.set_test_target(builder.build())
    test.start()
    time.sleep(30)
    test.stop()
    test.save_data()
