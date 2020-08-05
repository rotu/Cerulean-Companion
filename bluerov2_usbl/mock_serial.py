import itertools
import random
import time
from io import RawIOBase
from pathlib import Path

from serial import portNotOpenError
from serial import SerialBase, SerialException
import itertools


class MockSerial(SerialBase):
    data = None
    looped_data = None
    position = None

    @property
    def in_waiting(self):
        return 1

    def open(self):
        """
        Object which works like a serial port (as much as we can)
        """
        try:
            self.position = 0
            self.data = Path(self.port).read_bytes()
            self.looped_data = itertools.cycle(self.data)
            self.is_open = True
        except Exception as e:
            raise SerialException from e

    def read(self, size=1):
        if not self.is_open:
            raise portNotOpenError
        time.sleep(0.1*(size-1))
        return bytes(itertools.islice(self.looped_data, size))

    def _reconfigure_port(self):
        return

    def readable(self):
        return True

    def writable(self):
        return False

    def seekable(self):
        return False

    @property
    def closed(self):
        return not self.is_open

    def close(self, *args, **kwargs):
        self.is_open = False
