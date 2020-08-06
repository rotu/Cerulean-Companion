import logging
from typing import Callable

import pynmea2
import serial.threaded


class SerialNMEAProtocol(serial.threaded.LineReader):
    """
    NMEA Packetizer - breaks input on newline and calls callback on binary data
    """

    TERMINATOR = b'\r\n'
    ENCODING = 'ascii'
    nmea_callback = None

    def __init__(self, *, nmea_callback: Callable[[pynmea2.NMEASentence], None]):
        super().__init__()
        self.nmea_callback = nmea_callback

    def connection_made(self, transport):
        super().connection_made(transport)
        logging.info(f'Port opened: {transport.serial.name}')

    def connection_lost(self, exc):
        """Forget transport"""
        if exc:
            logging.error(f'closing port because of an error', exc_info=exc)
        logging.info(f'port closed')
        super().connection_lost(exc)

    def handle_line(self, data):
        logging.debug(f'Line received: {data!r}')
        try:
            sentence = pynmea2.NMEASentence.parse(data)
        except pynmea2.ParseError:
            logging.exception(f'Failed to parse as NMEA-0183 packet: {data}')
            return
        self.nmea_callback(sentence)
