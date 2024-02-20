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

    # The following configurations can be optionally set
    # 以下配置可选择设置

    # Upstream bandwidth(kbps)
    # 上行带宽,单位kbps
    option.outBandwidth.value = 1000
    # Upstream delay(ms)
    # 上行延时,单位毫秒
    option.outDelay.value = 1000
    # Uplink delay jitter
    # 上行延时抖动
    outDelayBias = option.outDelayBias.add()
    # The lower interval of the delay jitter range(ms)
    # 延时抖动范围的下区间,单位毫秒
    outDelayBias.delayBiasMin = 0
    # The upper interval of the delay jitter range(ms)
    # 延时抖动范围的上区间,单位毫秒
    outDelayBias.delayBiasMax = 1000
    # Probability of delay jitter 1-100%
    # 延时抖动的概率1-100%
    outDelayBias.delayBiasPercent = 50
    # Upstream random packet loss(integer type 1-100)
    # 上行随机丢包,1-100整型
    option.outRate.value = 100
    # Uplink periodic settings
    # If it is a complete packet loss, fill in outPass and outLoss, which correspond to the normal time and complete packet loss time respectively
    # If it is burst, fill in outPass and outBurst, which correspond to the normal time and the delayed effective time respectively (packets in the corresponding time period will not be sent out until the normal time arrives)
    # 上行周期性设置
    # 如果是完全丢包就填 outPass 和 outLoss ，分别对应正常时间和完全丢包时间
    # 如果是burst就填 outPass 和 outBurst，分别对应正常时间和延迟生效时间（对应时间段内的包会等到正常时间到来时才发出去）
    # Uplink periodic setting(normal release)(ms)
    # 上行周期性设置（正常放行）,单位毫秒
    option.outPass.value = 1000
    # Uplink periodic setting(complete packet loss)(ms)
    # 上行周期性设置（完全丢包）,单位毫秒
    option.outLoss.value = 1000
    # Uplink periodic setting(time point release)(ms)
    # 上行周期性设置（时间点放行）,单位毫秒
    option.outBurst.value = 1000

    # Downstream bandwidth(kbps)
    # 下行带宽,单位kbps
    option.inBandwidth.value = 1000
    # Downstream delay(kbps)
    # 下行延时,单位毫秒
    option.inDelay.value = 1000
    # Downstream delay jitter
    # 下行延时抖动
    inDelayBias = option.inDelayBias.add()
    # The lower interval of the delay jitter range(ms)
    # 延时抖动范围的下区间,单位毫秒
    inDelayBias.delayBiasMin = 0
    # The upper interval of the delay jitter range(ms)
    # 延时抖动范围的上区间,单位毫秒
    inDelayBias.delayBiasMax = 1000
    # Probability of delay jitter(1-100%)
    # 延时抖动的概率1-100%
    inDelayBias.delayBiasPercent = 50
    # Random downlink packet loss(integer type 1-100)
    # 下行随机丢包,1-100整型
    option.inRate.value = 100
    # Downstream periodic setting rules are the same as those for upstream
    # 下行周期性设置 规则同上行
    # Downlink periodic setting(normal release)(ms)
    # 下行周期性设置（正常放行）,单位毫秒
    option.inPass.value = 1000
    # Downlink periodicity setting(complete packet loss)(ms)
    # 下行周期性设置（完全丢包）,单位毫秒
    option.inLoss.value = 1000
    # Downlink periodic setting(time point release)(ms)
    # 下行周期性设置（时间点放行）,单位毫秒
    option.inBurst.value = 1000

    # Apply weak network simulation protocols, protocols not in the list will pass directly
    # 应用弱网模拟的协议,不在列表里的协议会直接通过
    option.affectedProtocol.append(perfdog_pb2.TCP)
    option.affectedProtocol.append(perfdog_pb2.UDP)
    option.affectedProtocol.append(perfdog_pb2.DNS)
    option.affectedProtocol.append(perfdog_pb2.ICMP)

    # Specify the IP of the weak network to take effect. If not added, it will take effect by default
    # 指定生效弱网的IP,不添加默认都生效
    option.ipList.append("127.0.0.1")

    return template


# todo
#Create a list of network templates for testing
# 创建测试用的网络模板列表
def create_templates(service):
    # Get the user's network template, including preset and user-defined ones
    # 获取用户的网络模板，包含预设的和用户自定义添加的
    templates = service.get_preset_network_template()
    for template in templates:
        logging.info("id:%d,name:%s,description:%s", template.id, template.name, template.description)

    # todo
    # Custom network templates can be created
    # 可以创建自定义网络模板
    user_template = create_customized_template()

    # Customized network templates can be uploaded to the server and can be obtained by calling get_preset_network_template next time
    # 自定义网络模板可以上传到服务器，下次调用get_preset_network_template可以获取到
    # service.submit_user_network_template(user_template)

    # todo
    # Select the network template for testing
    # 选择进行测试的网络模板
    test_templates = templates[3:7]
    test_templates.append(user_template)
    return test_templates


def main():
    # Log output configuration, you can configure it yourself if you have special needs
    # 日志输出配置，如果有特别的需要可自行配置
    logging.basicConfig(format="%(asctime)s-%(levelname)s: %(message)s", level=logging.INFO)

    # Create service object proxy
    # 创建服务对象代理
    service = create_service()

    # If the App has been installed on the device to be tested, please uninstall it from the device manually before continuing to use it
    # Network testing requires installing app
    # Enable installation
    # 如果App已经安装到要测试的设备上，请先手工从设备卸载之后继续使用
    # 网络测试需要安装app
    # 启用安装
    service.enable_install_apk()

    # TODO:
    # Fill in the correct device ID and the package name of the test app
    # You can use cmds.py in the same directory to obtain the list of devices connected to the computer and the App list of the corresponding devices
    # If you need to start collecting performance data for multiple devices in a single script process, you can run the run_test_app function multiple times in parallel through multi-threading
    # 填入正确的设备ID，填入测试app的包名
    # 可以使用同目录下cmds.py获取已连接到电脑的设备列表及相应设备的App列表
    # 如果单一脚本进程中需要启动针对多个设备性能数据收集，可以通过多线程的方式，并行运行多次run_test_app函数
    device = service.get_usb_device('-')
    if device is None:
        logging.error("device not found")
        return

    run_test_app(device, '-', create_templates(service))


def run_test_app(device, package_name, templates):
    # Create test object
    # 创建测试对象
    test = Test(device)

    # Create the target App to be tested
    # 创建要测试目标App
    builder = test.create_test_target_builder(TestAppBuilder)
    builder.set_package_name(package_name)
    builder.set_profiling_mode(perfdog_pb2.NETWORK)
    builder.set_network_template(templates[0])
    # Set whether the target app should be restarted or not, default is True.
    # 设置是否重新拉起目标App, 默认为True
    # builder.set_app_restarted(True)
    # Sets whether delays are superimposed or not, defaults to True.
    # 设置延迟是否叠加, 默认为True
    # builder.set_delay_overlay(True)
    test.set_test_target(builder.build())

    try:
        # Start performance data collection
        # 启动性能数据采集
        test.start()

        # Print the start test network template
        # 打印开始测试网络模板
        logging.info("start with network template: %s", templates[0].name)

        # TODO:
        # It is recommended to add automated test processing logic here
        # You can switch network templates multiple times during the test process
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
        # Release necessary resources
        # 必要的资源释放
        if test.is_start():
            test.stop()


if __name__ == '__main__':
    main()
