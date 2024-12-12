# coding: utf-8

import logging
import perfdog_pb2

from config import SERVICE_TOKEN, SERVICE_PATH
from perfdog import Service


def create_service(port=23456):
    service = Service(SERVICE_TOKEN, SERVICE_PATH, port=port)
    service.get_device_event_stream(lambda event: print_device(event))
    return service


def get_all_types(device):
    types, dynamicTypes = device.get_available_types()
    return [ty for ty in types], [(dynamicType.type, dynamicType.category) for dynamicType in dynamicTypes]


def set_floating_window(device):
    position = perfdog_pb2.HIDE
    font_color = perfdog_pb2.Color(red=0.49, green=0.93, blue=0.89, alpha=1.0)
    record_hotkey = ''
    add_label_hotkey = ''
    device.set_floating_window_preferences(position, font_color, record_hotkey, add_label_hotkey)


def print_device(event):
    if event.eventType == perfdog_pb2.ADD:
        logging.info("AddDevice: \n%s", event.device)
    elif event.eventType == perfdog_pb2.REMOVE:
        logging.info("RemoveDevice: \n%s", event.device)
