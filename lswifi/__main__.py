# -*- coding: utf-8 -*-

"""
lswifi.lswifi
~~~~~~~~~~~~~

a CLI Wi-Fi scanning utility for Windows that leverages Microsofts Native Wifi wlanapi.h
"""

import logging
import os
import platform
import sys

# hard set no support for non win32 platforms
if sys.platform == "win32":
    pass
else:
    print(f"{os.path.basename(__file__)} only works on win32... exiting...")
    sys.exit(-1)

# hard set no support for Python versions < 3.7
if sys.version_info < (3, 7):
    print(
        f"{os.path.basename(__file__)} requires Python 3.7+. "
        f"your active Python version is {platform.python_version()}. "
        f"exiting..."
    )
    sys.exit(-1)

# app imports
from lswifi import app, appsetup
from lswifi.__version__ import __title__
from lswifi.constants import APNAMEACKFILE, APNAMEJSONFILE


def app_path() -> None:
    appdata_path = os.path.join(os.getenv("LOCALAPPDATA"), __title__)  # type: ignore
    path_exists = os.path.isdir(appdata_path)
    if not path_exists:
        os.mkdir(appdata_path)
    print(f"{appdata_path}")


def main():
    is_apname_ack_stored = False
    parser = appsetup.setup_parser()
    args = parser.parse_args()
    appsetup.setup_logger(args)
    log = logging.getLogger(__name__)
    log.debug(f"args {args}")
    log.debug(f"{sys.version}")
    if args.data_location:
        app_path()
        sys.exit()
    if args.apnames:
        is_apname_ack_stored = user_ack_apnames_disclaimer()
        log.debug(
            f"is there a stored acknowledgement for caching apnames on local machine? {'Yes' if is_apname_ack_stored else 'No'}"
        )

    app.run(args, storedack=is_apname_ack_stored)


def user_ack_apnames_disclaimer() -> bool:
    """retrieve ack from user that BSSIDs and discovered apnames will be cached in appdata"""
    logger = logging.getLogger(__name__)
    if os.getenv("LOCALAPPDATA"):
        appdata_folder = os.path.join(os.getenv("LOCALAPPDATA"), __title__)  # type: ignore
    else:
        raise OSError
    is_path = os.path.isdir(appdata_folder)
    if not is_path:
        os.mkdir(appdata_folder)
        logger.debug("%s created? %s", appdata_folder, os.path.isdir(appdata_folder))
    ack = os.path.join(appdata_folder, APNAMEACKFILE)
    apnames = os.path.join(appdata_folder, APNAMEJSONFILE)
    if os.path.isfile(ack):
        return True
    else:
        print(
            "Running lswifi with --ap-names will cache detected AP names.\n\n"
            "Why?\n"
            "  - AP names are typically identified in beacon frames.\n"
            "  - The frame types in the scan results vary.\n"
            "  - Given data for a BSSID can be from a beacon or probe response.\n"
            "  - This is because a scan might not dwell on a channel long enough to hear a beacon.\n"
            "  - Dwell time varies per channel and can be shorter than the standard beacon interval.\n\n"
            "Where?\n"
            "  - Cached data is stored and read from a JSON file on your device here:\n\n"
            f"{apnames}\n"
        )
        try:
            text = input(
                "Please acknowledge storage and caching of AP names to enable feature (yes/no): "
            )
        except KeyboardInterrupt:
            print("\n\nDetected KeyboardInterrupt... Exiting...")
            sys.exit(-1)
        if "y" in text.lower()[:1]:
            with open(ack, "w") as file:
                pass  # we only need a placeholder file
            print(
                "\nAP name caching is now enabled and we've recorded your response here: \n\n"
                f"{ack}\n\n"
                "If you'd like to disable this feature delete the file.\n"
            )
            return True
        else:
            return False


def init() -> None:
    """Handle main init."""
    if __name__ == "__main__":
        main()
        sys.exit(0)


init()
