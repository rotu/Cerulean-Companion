import argparse
import logging
import os
import time

from bluerov2_usbl.usbl_relay_controller import list_serial_ports, USBLController

parser = argparse.ArgumentParser(
    description='Cerulean companion: Listen for a GPS position of a base station '
                'and relative position data from that base station to the ROVL Transmitter. Relay the '
                'GPS data unchanged to QGroundControl and compute the absolute position data '
                'to the ROVL Transmitter. ')

parser.add_argument(
    '-r', '--rovl', help="Port of the ROVL Receiver", type=str,
    metavar='COM#' if os.name == 'nt' else '/dev/ttyUSB#', required=False)
parser.add_argument(
    '-g', '--gps', help='Port of the GPS device', type=str,
    metavar='COM#' if os.name == 'nt' else '/dev/ttyXXX#', required=False)
parser.add_argument(
    '-e', '--echo', help='UDP Address to pass GPS data to',
    metavar='127.0.0.1:14401', required=False)
parser.add_argument(
    '-m', '--mav', help='UDP Address to send ROVL position to', metavar='192.168.2.2:27000',
    required=False)
parser.add_argument(
    '--log', '-l', metavar='level', default='info',
    choices=['error', 'warning', 'info', 'debug'],
    help='How verbose should we be?')


def get_serial_device_summary():
    result = [
        'Serial devices detected:',
        *['  ' + str(p) for p in list_serial_ports()]
    ]
    return '\r\n'.join(result)


args = parser.parse_args()

if args.rovl is None or args.gps is None:
    parser.error("GPS and ROVL devices must be specified\n\n" + get_serial_device_summary())

logging.basicConfig(
    level=args.log.upper(),
    format='%(threadName)-5s %(levelname)-8s %(message)s'
)

c = USBLController()
c.set_change_callback(lambda key, value: logging.info(f'{key} is now {value}'))
c.dev_usbl = args.rovl
c.dev_gps = args.gps
c.addr_echo = args.echo
c.addr_mav = args.mav

while True:
    time.sleep(0.1)
