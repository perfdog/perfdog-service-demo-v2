# coding: utf-8

import sys

import perfdog_pb2
from perfdog import Service
from config import SERVICE_TOKEN, SERVICE_PATH


def print_devices(service):
    for device in service.get_devices():
        print(device)


def print_apps(service, device_id):
    device = service.get_usb_device(device_id)
    if device is None:
        device = service.get_wifi_device(device_id)
        if device is None:
            return

    status = device.get_status()
    if not status.isValid:
        device.init()

    for app in device.get_apps():
        print(app.packageName, app.label)


def print_sys_processes(service, device_id):
    device = service.get_usb_device(device_id)
    if device is None:
        device = service.get_wifi_device(device_id)
        if device is None:
            return

    status = device.get_status()
    if not status.isValid:
        device.init()

    for process in device.get_sys_processes():
        print(process.pid, process.name)


def print_types(service, device_id):
    device = service.get_usb_device(device_id)
    if device is None:
        device = service.get_wifi_device(device_id)
        if device is None:
            return

    status = device.get_status()
    if not status.isValid:
        device.init()

    types, dynamicTypes = device.get_available_types()
    for index, ty in enumerate(types):
        try:
            print('type[{}]: perfdog_pb2.{}'.format(index, perfdog_pb2.PerfDataType.Name(ty)))
        except ValueError:
            pass

    for index, dynamicType in enumerate(dynamicTypes):
        try:
            print('dynamicType[{}]: perfdog_pb2.{}, {}'.format(
                index,
                perfdog_pb2.DynamicPerfDataType.Name(dynamicType.type),
                dynamicType.category))
        except ValueError:
            pass


def kill_server(service):
    service.kill_server()


def print_preset_network_template(service):
    templates = service.get_preset_network_template()
    for template in templates:
        print('id:{},name:{},description:{}'.format(template.id, template.name, template.description))


def print_usage():
    print('usage: python cmds.py getdevices')
    print('       python cmds.py getapps device_id')
    print('       python cmds.py getsysprocesses device_id')
    print('       python cmds.py gettypes device_id')
    print('       python cmds.py killserver')
    print('       python cmds.py getpresetnetworktemplate')


def get_func_and_args(args):
    if len(args) == 0:
        return None, ()

    cmd = args[0]
    args = args[1:]

    if cmd == 'getdevices' and len(args) == 0:
        return print_devices, args

    if cmd == 'getapps' and len(args) == 1:
        return print_apps, args

    if cmd == 'getsysprocesses' and len(args) == 1:
        return print_sys_processes, args

    if cmd == 'gettypes' and len(args) == 1:
        return print_types, args

    if cmd == 'killserver' and len(args) == 0:
        return kill_server, args

    if cmd == 'getpresetnetworktemplate' and len(args) == 0:
        return print_preset_network_template, args

    return None, ()


def main():
    func, args = get_func_and_args(sys.argv[1:])
    if func is None:
        print_usage()
        return

    service = Service(SERVICE_TOKEN, SERVICE_PATH)
    func(service, *args)


if __name__ == '__main__':
    main()
