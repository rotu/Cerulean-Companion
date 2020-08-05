import json
import logging
from functools import wraps
from pathlib import Path

import pkg_resources
import webview

from bluerov2_usbl.usbl_relay_controller import USBLController, list_serial_ports

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def js_function(stub: callable):
    """Decorator for a function callable from Python whose implementation actually lives in Javascript"""

    @wraps(stub)
    def wrapper(*args, **kwargs):
        assert not args or not kwargs
        if kwargs:
            argstr = json.dumps(kwargs)
        else:
            argstr = ','.join(json.dumps(a) for a in args)
        snippet = f'{stub.__name__}({argstr})'
        return window.evaluate_js(snippet)

    return wrapper


@js_function
def add_to_log(severity, message): ...


@js_function
def on_list_usb_devices(values): ...


@js_function
def on_controller_attr_changed(attr, value): ...


class Api:
    def __init__(self):
        self.usbl_controller = USBLController()
        self.usbl_controller.set_change_callback(lambda x, y: None)

    def get_serial_devices(self):
        return [cp.__dict__ for cp in list_serial_ports()]

    def connect(self, obj):
        self.usbl_controller.start(
            rovl_port=obj['rovl_port'],
            gps_port=obj['gps_port'],
            gps_baud=obj['gps_baud'],
            addr_gcs=obj['addr_gcs'],
            addr_rov=obj['addr_rov'],
        )

    def disconnect(self):
        self.usbl_controller.stop()

    def sync_location(self):
        self.usbl_controller.sync_location()


main_html = pkg_resources.resource_filename('bluerov2_usbl', 'web/main.html')
window = webview.create_window('Cerulean Companion: usbl controller', Path(main_html), js_api=Api())


class AppLoggingHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        add_to_log(record.levelname.lower(), record.msg)


logging.basicConfig(
    level='INFO',
    handlers=[AppLoggingHandler(), logging.StreamHandler()]
)

webview.start(http_server=True, debug=True)
