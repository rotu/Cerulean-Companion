import logging
import sys
import time
from argparse import RawDescriptionHelpFormatter

from gooey import GooeyParser

from bluerov2_usbl.usbl_relay_controller import list_serial_ports, USBLController


def get_serial_device_summary():
    result = [
        'Serial devices detected:',
        *['  ' + str(p) for p in list_serial_ports()]
    ]
    return '\r\n'.join(result)


def main():
    parser = GooeyParser(
        description='Listen for a GPS position of a base station '
                    'and relative position data from that base station to the ROVL Transmitter. Relay the '
                    'GPS data unchanged to QGroundControl and compute the absolute position data '
                    'to the ROVL Transmitter. ',

        formatter_class=RawDescriptionHelpFormatter,
        epilog=get_serial_device_summary(),
    )

    devices = parser.add_argument_group('Input')
    devices.add_argument(
        '--rovl', '-r', help="Port of the ROVL Receiver",
        widget='Dropdown',
        metavar='ROVL',
        required=True)
    devices.add_argument(
        '--gps', '-g', help='Port of the GPS device',
        widget='Dropdown',
        metavar='GPS',
        required=True)
    devices.add_argument(
        '-b', '--baud', help='Baud rate of the GPS device',
        type=int,
        widget='Dropdown',
        metavar='BAUD',
        default=9600,
        choices=[1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200])

    output = parser.add_argument_group('output')
    output.add_argument(
        '-e', '--echo', help='UDP Address to repeat GPS data to', metavar="echo address",
        default='127.0.0.1:14401', required=False)
    output.add_argument(
        '-m', '--mav', help='UDP Address to send ROVL position to', metavar='MAV address', default='192.168.2.2:27000',
        required=False)
    output.add_argument(
        '--log', '-l', metavar='level', default='info',
        choices=['error', 'warning', 'info', 'debug'],
        help='How verbose should we be?',
        gooey_options={'visible': False})

    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)

    args = parser.parse_args()

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
