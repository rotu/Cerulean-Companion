import json
import logging
from functools import wraps
from pathlib import Path

import pkg_resources
import webview

from bluerov2_usbl.usbl_relay_controller import USBLController, list_serial_ports

logger = logging.getLogger()
logger.setLevel(logging.INFO)

usbl_controller = USBLController()


class Api:
    def controller_set_attr(self, obj):
        (attr, value), = obj.items()
        print(f'setting {attr}={value}')

        try:
            setattr(usbl_controller, attr, value)
        except Exception as e:
            logger.error(str(e))

    def get_serial_devices(self):
        return [cp.device for cp in list_serial_ports()]


main_html = pkg_resources.resource_filename('bluerov2_usbl', 'web/main.html')
window = webview.create_window('USBL controller', Path(main_html), js_api=Api())


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
def on_controller_attr_changed(attr, value): ...


@js_function
def on_list_usb_devices(values): ...


class AppLoggingHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        add_to_log(record.levelname.lower(), record.msg)


logging.basicConfig(
    level='INFO',
    handlers=[AppLoggingHandler(), logging.StreamHandler()]
)

usbl_controller.set_change_callback(on_controller_attr_changed)

webview.start(http_server=True, debug=True)
