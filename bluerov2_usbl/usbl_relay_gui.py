import json
import logging
import traceback
from functools import wraps
from pathlib import Path

import pkg_resources
import webview

from bluerov2_usbl.usbl_relay_controller import ROVLController, list_serial_ports

logger = logging.getLogger()


def main():
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
    def add_to_log(severity, message, detail):
        ...

    @js_function
    def on_list_usb_devices():
        ...

    class Api:
        def __init__(self):
            self.usbl_controller = None

        def get_serial_devices(self):
            return [cp.__dict__ for cp in list_serial_ports()]

        def connect(self, obj):
            self.usbl_controller = ROVLController(
                rovl_port=obj['rovl_port'],
                rovl_serial_kwargs={},
                gps_port=obj['gps_port'],
                gps_serial_kwargs={'baudrate': obj['gps_baud']} if obj['gps_baud'] else {},
                addr_gcs=(obj['gcs_host'], obj['gcs_port']) if obj['gcs_host'] else None,
                addr_rov=(obj['rov_host'], obj['rov_port']) if obj['rov_host'] else None,
            )

        def disconnect(self):
            self.usbl_controller.stop()

        def sync_location(self):
            self.usbl_controller.sync_location()

    main_html = pkg_resources.resource_filename('bluerov2_usbl', 'web/index.html')
    window = webview.create_window('Cerulean Companion: usbl controller', Path(main_html), js_api=Api(),
                                   text_select=True)

    class AppLoggingHandler(logging.Handler):
        def emit(self, record: logging.LogRecord):
            detail = None
            if record.exc_info:
                detail = ''.join(traceback.format_exception(*record.exc_info))
            add_to_log(record.levelname.lower(), record.msg, detail)

    logging.basicConfig(
        level='INFO',
        handlers=[logging.StreamHandler(), AppLoggingHandler()]
    )

    webview.start(http_server=True, debug=True)


if __name__ == '__main__':
    main()
