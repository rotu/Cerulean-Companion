from gooey import GooeyParser

import logging
import os
import time

from serial.tools.list_ports_common import ListPortInfo

from bluerov2_usbl.usbl_relay_controller import list_serial_ports, USBLController



def get_serial_device_summary():
    result = [
        'Serial devices detected:',
        *['  ' + str(p) for p in list_serial_ports()]
    ]
    return '\r\n'.join(result)

def main():
    parser = GooeyParser(
            description='Cerulean companion: Listen for a GPS position of a base station '
                        'and relative position data from that base station to the ROVL Transmitter. Relay the '
                        'GPS data unchanged to QGroundControl and compute the absolute position data '
                        'to the ROVL Transmitter. ')

    parser.add_argument(
        '--rovl','-r', help="Port of the ROVL Receiver",
        choices=[],
        widget='Dropdown',
        metavar='ROVL',
        required=True)
    parser.add_argument(
        '--gps','-g', help='Port of the GPS device',
        choices=[],
        widget='Dropdown',
        metavar='GPS',
        required=True)

    parser.add_argument(
        '-e', '--echo', help='UDP Address to pass GPS data to', metavar="echo address",
     default='127.0.0.1:14401', required=False)
    parser.add_argument(
        '-m', '--mav', help='UDP Address to send ROVL position to', metavar='MAV address', default='192.168.2.2:27000',
        required=False)
    parser.add_argument(
        '--log', '-l', metavar='level', default='info',
        choices=['error', 'warning', 'info', 'debug'],
        help='How verbose should we be?')

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

if __name__ == '__main__':
    main()