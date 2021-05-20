# coding: utf-8

import sys
from perfdog import Service
from config import SERVICE_TOKEN, SERVICE_PATH


def print_devices(service):
    for device in service.get_devices():
        print(device)


def print_apps(service, device_id):
    device = service.get_usb_device(device_id)
    if device is None:
        return

    status = device.get_status()
    if not status.isValid:
        device.init()

    for app in device.get_apps():
        print(app.packageName)


def print_usage():
    print('usage: python cmds.py getdevices')
    print('       python cmds.py getapps device_id')


def get_func_and_args(args):
    if len(args) == 0:
        return None, ()

    cmd = args[0]
    args = args[1:]

    if cmd == 'getdevices' and len(args) == 0:
        return print_devices, args

    if cmd == 'getapps' and len(args) == 1:
        return print_apps, args

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
