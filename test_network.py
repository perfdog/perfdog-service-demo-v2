# coding: utf-8

import logging
import time

import perfdog_pb2
from perfdog import Test, TestAppBuilder
from test_base import create_service


def create_customized_template():
    template = perfdog_pb2.NetworkProfilingTemplate()
    template.name = "test"
    template.description = "test"

    option = template.networkProfilingOptions.add()

    # 以下配置可选择设置
    option.outBandwidth.value = 1000  # 上行带宽,单位kbps
    option.outDelay.value = 1000  # 上行延时,单位毫秒
    outDelayBias = option.outDelayBias.add()  # 上行延时抖动
    outDelayBias.delayBiasMin = 0  # 延时抖动范围的下区间,单位毫秒
    outDelayBias.delayBiasMax = 1000  # 延时抖动范围的上区间,单位毫秒
    outDelayBias.delayBiasPercent = 50  # 延时抖动的概率1-100%
    option.outRate.value = 100  # 上行随机丢包,1-100整型
    option.outPass.value = 1000  # 上行周期性设置（正常放行）,单位毫秒
    option.outLoss.value = 1000  # 上行周期性设置（完全丢包）,单位毫秒
    option.outBurst.value = 1000  # 上行周期性设置（时间点放行）,单位毫秒

    option.outBandwidth.value = 1000  # 下行带宽,单位kbps
    option.outDelay.value = 1000  # 下行延时,单位毫秒
    outDelayBias = option.outDelayBias.add()  # 下行延时抖动
    outDelayBias.delayBiasMin = 0  # 延时抖动范围的下区间,单位毫秒
    outDelayBias.delayBiasMax = 1000  # 延时抖动范围的上区间,单位毫秒
    outDelayBias.delayBiasPercent = 50  # 延时抖动的概率1-100%
    option.outRate.value = 100  # 下行随机丢包,1-100整型
    option.outPass.value = 1000  # 下行周期性设置（正常放行）,单位毫秒
    option.outLoss.value = 1000  # 下行周期性设置（完全丢包）,单位毫秒
    option.outBurst.value = 1000  # 下行周期性设置（时间点放行）,单位毫秒

    option.affectedProtocol.append(perfdog_pb2.TCP)  # 应用弱网模拟的协议,不在列表里的协议会直接通过
    option.affectedProtocol.append(perfdog_pb2.UDP)
    option.affectedProtocol.append(perfdog_pb2.DNS)
    option.affectedProtocol.append(perfdog_pb2.ICMP)

    option.ipList.append("127.0.0.1")  # 指定生效弱网的IP,不添加默认都生效

    return template


# todo
# 创建测试用的网络模板列表
def create_templates(service):
    # 获取用户的网络模板，包含预设的和用户自定义添加的
    templates = service.get_preset_network_template()
    for template in templates:
        logging.info("id:%d,name:%s,description:%s", template.id, template.name, template.description)

    # todo
    # 可以创建自定义网络模板
    user_template = create_customized_template()

    # 自定义网络模板可以上传到服务器，下次调用get_preset_network_template可以获取到
    # service.submit_user_network_template(user_template)

    # todo
    # 选择进行测试的网络模板
    test_templates = templates[3:7]
    test_templates.append(user_template)
    return test_templates


def main():
    # 日志输出配置，如果有特别的需要可自行配置
    logging.basicConfig(format="%(asctime)s-%(levelname)s: %(message)s", level=logging.INFO)

    # 创建服务对象代理
    service = create_service()

    # 如果App已经安装到要测试的设备上，请先手工从设备卸载之后继续使用
    # 网络测试需要安装app
    # 启用安装
    service.enable_install_apk()

    # TODO:
    # 填入正确的设备ID，填入测试app的包名
    # 可以使用同目录下cmds.py获取已连接到电脑的设备列表及相应设备的App列表
    # 如果单一脚本进程中需要启动针对多个设备性能数据收集，可以通过多线程的方式，并行运行多次run_test_app函数
    device = service.get_usb_device('-')
    if device is None:
        logging.error("device not found")
        return

    run_test_app(device, '-', create_templates(service))


def run_test_app(device, package_name, templates):
    # 创建测试对象
    test = Test(device)

    # 创建要测试目标App
    builder = test.create_test_target_builder(TestAppBuilder)
    builder.set_package_name(package_name)
    builder.set_profiling_mode(perfdog_pb2.NETWORK)
    builder.set_network_template(templates[0])
    test.set_test_target(builder.build())

    try:
        # 启动性能数据采集
        test.start()

        # 打印开始测试网络模板
        logging.info("start with network template: %s", templates[0].name)

        # TODO:
        # 建议在此处添加自动化测试处理逻辑
        # 测试过程中可以多次切换网络模板
        for template in templates[1:]:
            time.sleep(10)
            test.set_label(template.name)
            device.change_network_template(template)
            logging.info("change network template: %s", template.name)

        time.sleep(2)
        test.stop()

    finally:
        # 必要的资源释放
        if test.is_start():
            test.stop()


if __name__ == '__main__':
    main()
