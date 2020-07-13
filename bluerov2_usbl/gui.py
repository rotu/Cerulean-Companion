import sys


def main():
    if 'gooey-seed-ui' in sys.argv:
        import json
        from bluerov2_usbl.usbl_relay_controller import list_serial_ports

        serial_ports = [r.device for r in list_serial_ports()]

        json.dump({
            '--rovl': serial_ports,
            '--gps': serial_ports,
        }, sys.stdout)
    else:
        import bluerov2_usbl.cli
        import gooey
        import pkg_resources

        gooey_main = gooey.Gooey(
            bluerov2_usbl.cli.main,
            poll_external_updates=True,
            image_dir=pkg_resources.resource_filename('bluerov2_usbl', 'resources/gooey_image_dir'),
            header_bg_color='#1dacd6',
            program_name='Cerulean Companion',
            force_stop_is_error=False,
            show_stop_warning=False,
            show_success_modal=False,
            show_failure_modal=False,
            program_description='Fuse GPS and USBL data',
        )

        gooey_main()


if __name__ == '__main__':
    main()
