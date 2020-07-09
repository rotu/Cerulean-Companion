from gooey import Gooey

import bluerov2_usbl.usbl_relay_cli

gooey_main = Gooey(bluerov2_usbl.usbl_relay_cli.main)

if __name__ == '__main__':
    gooey_main()