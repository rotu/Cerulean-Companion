import itertools
import logging
import time
from pathlib import Path

from serial import SerialBase, SerialException
from serial import portNotOpenError


class MockSerial(SerialBase):
    data = None
    looped_data = None
    position = None

    def cancel_read(self):
        pass

    @property
    def in_waiting(self):
        return 1

    def open(self):
        """
        Object which works like a serial port (as much as we can)
        """
        try:
            self.position = 0
            lines = Path(self.port).read_bytes().splitlines()
            # filtern out blank lines
            lines = [line for line in lines if line]
            self.data = b''.join(line + b'\r\n' for line in lines if line)
            self.looped_data = itertools.cycle(self.data)
            self.is_open = True
        except Exception as e:
            raise SerialException from e

    def read(self, size=1):
        if not self.is_open:
            raise portNotOpenError
        time.sleep(0.1 * (size - 1))
        return bytes(itertools.islice(self.looped_data, size))

    def write(self, data):
        logging.debug(f'Pretending to write {data}')

    def _reconfigure_port(self):
        return

    def readable(self):
        return True

    def writable(self):
        return True

    def seekable(self):
        return False

    @property
    def closed(self):
        return not self.is_open

    def close(self, *args, **kwargs):
        self.is_open = False
