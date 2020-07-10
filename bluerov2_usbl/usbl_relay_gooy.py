import sys

if __name__ == '__main__':
    if 'gooey-seed-ui' in sys.argv:
        import json
        from bluerov2_usbl.usbl_relay_controller import list_serial_ports

        serial_ports = [str(r) for r in list_serial_ports()]

        print(json.dumps({
            '--rovl': [serial_ports],
            '--gps': [serial_ports]
        }))
    else:
        import bluerov2_usbl.usbl_relay_cli
        import gooey
        import pkg_resources

        gooey_main = gooey.Gooey(
            bluerov2_usbl.usbl_relay_cli.main,
            poll_external_updates=True,
            image_dir=pkg_resources.resource_filename(__name__, 'resources/gooey_image_dir'),
            header_bg_color='#1dacd6', program_name='USBL Relay')

        gooey_main()
