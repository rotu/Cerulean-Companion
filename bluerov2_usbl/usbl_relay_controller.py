import contextlib
import logging
import socket
from collections import ChainMap
from functools import partial
from math import cos, radians, sin, degrees
from typing import Optional, Tuple

from pynmea2 import ChecksumError, NMEASentence, ParseError, RMC, RTH, SentenceTypeError
from serial.threaded import LineReader, ReaderThread
from serial.tools import list_ports

from bluerov2_usbl.mock_serial import MockSerial

DEFAULT_ROVL_BAUDRATE = 115200
DEFAULT_GPS_BAUDRATE = 4800


def degrees_to_sdm(signed_degrees: float) -> (bool, int, float):
    """
    converts signed fractional degrees to triple: is_positive, int_degrees, minutes
    """
    unsigned_degrees = abs(signed_degrees)
    return (
        signed_degrees >= 0,
        int(unsigned_degrees),
        (unsigned_degrees * 60) % 60
    )


#
# def lat_lon_per_meter(current_latitude_degrees):
#     """Returns the number of degrees per meter, in latitude and longitude"""
#     # # based on https://en.wikipedia.org/wiki/Geographic_coordinate_system#Length_of_a_degree
#     # phi = radians(current_latitude_degrees)
#     # meters_per_lat = 111132.92 - 559.82 * cos(2 * phi) + 1.175 * cos(4 * phi) - 0.0023 * cos(
#     #     6 * phi)
#     # meters_per_lon = 111412.84 * cos(phi) - 93.5 * cos(3 * phi) + 0.118 * cos(5 * phi)
#
#     #https://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude
#     -longitude-by-some-amount-of-meters/2968
#     R = 6378137
#     lat_per_meter = degrees(1/R)
#     lon_per_meter = degrees(1/(R*cos(radians(current_latitude_degrees))))
#
#     return lat_per_meter, lon_per_meter
#

def combine_rmc_rth(rmc: RMC, rth: RTH) -> RMC:
    compass_bearing = rth.cb
    slant_range = rth.sr
    true_elevation = rth.te

    horizontal_range = slant_range * cos(radians(true_elevation))

    dn = cos(radians(compass_bearing)) * horizontal_range
    de = sin(radians(compass_bearing)) * horizontal_range
    R = 6378137

    dLat = dn / R
    dLon = de / (R * cos(radians(rmc.latitude)))

    new_lat = rmc.latitude + degrees(dLat)
    new_lon = rmc.longitude + degrees(dLon)

    # newLatDegrees, newLatMinutes = ddToDDM(newLat)
    # newLonDegrees, newLonMinutes = ddToDDM(newLon)

    # d_lat, d_lon = lat_lon_per_meteddr(rmc.latitude)
    # new_lat = rmc.latitude + cos(radians(compass_bearing)) * horizontal_range * d_lat
    # new_lon = rmc.longitude + sin(radians(compass_bearing)) * horizontal_range * d_lon
    lat_sgn, lat_deg, lat_min = degrees_to_sdm(new_lat)
    lon_sgn, lon_deg, lon_min = degrees_to_sdm(new_lon)
    new_rmc_data = [
        *rmc.data[:2],
        f'{lat_deg:02d}{lat_min:06.3f}',
        {True: 'N', False: 'S'}[lat_sgn],
        f'{lon_deg:02d}{lon_min:06.3f}',
        {True: 'E', False: 'W'}[lon_sgn],
        '',
        '',
        *rmc.data[8:]
    ]
    return RMC('GN', 'RMC', new_rmc_data)


def list_serial_ports():
    return list(list_ports.comports())


class ReaderProtocolFactory(LineReader):
    TERMINATOR = b'\r\n'
    ENCODING = 'ascii'

    def __init__(self, line_callback):
        super().__init__()
        self.line_callback = line_callback

    def connection_made(self, transport):
        super().connection_made(transport)
        logging.info(f'Port opened: {transport.serial.name}')

    def handle_line(self, data):
        logging.debug(f'line received: {data!r}')
        self.line_callback(data)

    def connection_lost(self, exc):
        if exc:
            logging.error(f'closing port because of an error', exc_info=exc)

        logging.info(f'port closed')


class ROVLController:
    _addr_gcs: Optional[Tuple[str, int]] = None
    _addr_rov: Optional[Tuple[str, int]] = None

    _last_rmc: Optional[RMC] = None

    _stopping = False

    def __init__(self,
                 rovl_port, rovl_serial_kwargs,
                 gps_port, gps_serial_kwargs,
                 addr_gcs: Optional[Tuple[str, int]],
                 addr_rov: Optional[Tuple[str, int]]
                 ):

        self._addr_gcs = addr_gcs
        self._addr_rov = addr_rov
        self._stopping = False

        self._out_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._out_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._out_udp.setblocking(False)

        rovl_kwargs = ChainMap(rovl_serial_kwargs, {'baudrate': DEFAULT_ROVL_BAUDRATE})
        dev_usbl = MockSerial(rovl_port, **rovl_kwargs)

        gps_kwargs = ChainMap(gps_serial_kwargs, {'baudrate': DEFAULT_GPS_BAUDRATE})
        dev_gps = MockSerial(gps_port, **gps_kwargs)

        self.gps_worker = ReaderThread(
            dev_gps,
            partial(ReaderProtocolFactory,
                    line_callback=self._on_gps_line, )
        )
        self.gps_worker.name = 'GPS Reader'
        self.gps_worker.start()

        self.rovl_worker = ReaderThread(
            dev_usbl,
            partial(ReaderProtocolFactory,
                    line_callback=self._on_usbl_line)
        )
        self.rovl_worker.name = 'ROVL Reader'
        self.rovl_worker.start()

    def sync_location(self):
        logging.info(f'Syncing location of ROVL and GPS...')
        self.rovl_worker.serial.write(b'D0\r\n')

    def _on_gps_line(self, ln):
        addr_gcs = self._addr_gcs
        try:
            if addr_gcs is not None:
                self._out_udp.sendto(ln.encode(), addr_gcs)
        except OSError:
            if not self._stopping:
                raise

        if ln[3:6] != 'RMC':
            return
        try:
            rmc = NMEASentence.parse(ln)
        except ChecksumError:
            logging.debug(f'Ignoring message with bad checksum: {ln}')
            return
        except SentenceTypeError:
            logging.debug(f'Ignoring message with unrecognized sentence type: {ln}')
            return
        except ParseError:
            return
        if not rmc.is_valid:
            logging.info(f'No GPS fix.')
            return

        self._last_rmc = rmc

    def _on_usbl_line(self, ln):
        if self._stopping:
            logging.debug(f'Ignoring USBL data. Stopping...')
            return

        rth = NMEASentence.parse(ln)
        logging.debug(f'RTH: {ln}')
        if rth.sentence_type != 'RTH':
            logging.debug(f'Ignoring unexpected message from USBL. Expected a RTH sentence: {rth}')
            return

        rmc = self._last_rmc
        if rmc is None:
            logging.info('Ignoring RTH message because we do not yet have a location (RMC message) from the ROVL')
            return

        addr_rov = self._addr_rov
        if addr_rov is None:
            return

        new_rmc = combine_rmc_rth(rmc, rth)
        self._out_udp.sendto(str(new_rmc).encode('ascii') + b'\r\n', addr_rov)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def stop(self):
        if self._stopping:
            logging.warning('ROVL controller already stopped')
            return

        logging.info('Stopping ROVL controller...')
        self._stopping = True
        with contextlib.ExitStack() as stack:
            self.gps_worker.alive = False
            self.rovl_worker.alive = False

            stack.callback(self.gps_worker.close)
            stack.callback(self.rovl_worker.close)
            stack.callback(self._out_udp.close)
