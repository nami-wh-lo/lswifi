# -*- coding: utf-8 -*-

"""
lswifi.appsetup
~~~~~~~~~~~~~~~

Provides init functions that are used to help set up the app.
"""

import argparse
import datetime
import ipaddress
import logging
import logging.config
import os
import sys
import textwrap
import time
from pathlib import Path

from lswifi import slog
from lswifi.__version__ import __version__


class ExportAction(argparse.Action):
    """Enable export argument

    Adds support for bool or bssid
    """

    def __call__(self, parser, namespace, values, option_string=None):
        """If no values, return something arbitrary so the arg is not None."""
        if not values:
            values = "all"
        setattr(namespace, self.dest, values)


BOOT_TIME = (
    datetime.datetime.now()
    .astimezone()
    .replace(microsecond=0)
    .isoformat()
    .replace(":", "_")
)


def VerifyPath(_path, _extension):
    # if absolute path is a directory and not a file
    if os.path.isdir(_path):
        print(f"{_path} is a directory not a file. exiting...")
        sys.exit(-1)
    # ensure we're writing to a file ending with .csv
    if not _path.lower().endswith(_extension):
        print(f"Exiting because file does not end with {_extension}")
        sys.exit(-1)
    # parent of the path exists?
    if Path(_path).parent.absolute().exists():
        # do we actually have write access?
        try:
            temp_file_path = (
                Path(_path).parent.absolute()
                / f"lswifi_write_test_{int(time.time() * 1000)}.tmp"
            )
            file_out = open(temp_file_path, "w")
            file_out.close()
            os.remove(temp_file_path)
        except PermissionError:
            if Path(_path).is_absolute():
                print(f"Problem with write permission to {_path}. exiting...")
            else:
                print(
                    f"Problem with write permission in {Path(_path).parent.absolute()} for {_path}. exiting..."
                )
            sys.exit(-1)
    # does the parent directory of the path provided actually exist?
    if Path(_path).is_absolute():
        if not Path(_path).parent.absolute().exists():
            print(
                f"Parent directory at {Path(_path).parent.absolute()} does not exist. exiting..."
            )
            sys.exit(-1)


class WriteToCSVAction(argparse.Action):
    """Enable write to file arguments

    Intended for CSV and JSON options
    """

    def __call__(self, parser, namespace, values, option_string=None):
        """If no values, return something arbitrary so the arg is not None."""
        if not values:
            values = f"lswifi_{BOOT_TIME}.csv"
        VerifyPath(values, ".csv")
        setattr(namespace, self.dest, values)


class WriteToJSONAction(argparse.Action):
    """Enable write to file arguments

    Intended for CSV and JSON options
    """

    def __call__(self, parser, namespace, values, option_string=None):
        """If no values, return something arbitrary so the arg is not None."""
        if not values:
            values = f"lswifi_{BOOT_TIME}.json"
        VerifyPath(values, ".json")
        setattr(namespace, self.dest, values)


def setup_logger(args) -> logging.Logger:
    """Set up the logger"""
    default_logging = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}
        },
        "handlers": {
            "default": {
                "level": args.debug,
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            }
        },
        "loggers": {"": {"handlers": ["default"], "level": args.debug}},
    }
    logging.config.dictConfig(default_logging)
    return logging.getLogger(__name__)


def sensitivity(value):
    """Validate user provided sensitivity is between -1 (stronger) and -100 (weaker)"""
    try:
        display_sensitivity = int(value)
        if display_sensitivity not in range(-100, 0):
            raise argparse.ArgumentTypeError(
                "rssi sensitivity threshold must be a value from -1 to -100"
            )
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} not a valid threshold")
    return display_sensitivity


def json_indent(value):
    """Validate user provided pretty print json value is sane and between 0 and 4"""
    try:
        if value is None:
            return None
        indent_level = int(value)
        if indent_level not in range(0, 5):
            raise argparse.ArgumentTypeError("JSON indent level must be less than 5")
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} not a valid JSON indent level")
    return indent_level


def width(value):
    """Validate user provided channel bandwidth is 5, 10, 20, 40, 80, or 160"""
    valid_channels = [ "5","10","20", "40", "80", "160"]
    if value == "None":
        return None

    width = str(value)
    if width not in valid_channels:
        raise argparse.ArgumentTypeError(
            f"channel width {width} not valid. must use one of these: {', '.join(valid_channels)}"
        )
    return width


def syslog_ip(value):
    """Validate user provided IP is actually an IP address"""
    if value == "None":
        return None
    try:
        servers = []
        for ip in value.split(","):
            ipaddress.ip_address(ip)
            servers.append(ip)
        slog.SYSLOG_SERVERS = servers
        return servers  # return something so the arg is not None
    except ValueError:
        raise argparse.ArgumentTypeError("IP address {} is not valid".format(value))


def setup_parser() -> argparse.ArgumentParser:
    """Sets up the parser for arguments passed into the module from the CLI.

    Returns:
        argparse object.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """   
                               ..:--==+++++++++++++==--:.
                          .-=++++++++++++++++++++++++++++++=-:.
                      :-++++++++++++++++++++++++++++++++++++++++=-.
                  .:=++++++++++++++++===---------==+++++++++++++++++=:
                :=++++++++++++=-:..                   .::-=++++++++++++=:
             .-+++++++++++=:.                               .:=+++++++++++-
            -++++++++++-.         .:--==+++++++++==-::.         .-++++++++++-
             :++++++++++:    .-=+++++++++++++++++++++++++=:.       .=++++++: .---:
       :*%+.   -++++++++++-=+++++++++++++++++++++++++++++++++=:       -++: :#@@@@@%+
     :*@@@@%+.   -++++++++++++++++++++++=========+++++++++++++++=.        .%@@@@@@@@*
   .*@@@@@@@@%+.   -+++++++++++++=-:.              ..:=++++++++++++:      :@@@@@@@@@%
    -%@@@@@@@@@%+.   -++++++++-:                         :=++++++++:   .+: +@@@@@@@%:
      -%@@@@@@@@@%+.   -+++=.         .::-------::.       -++++++:   .*@@@*:.=+**+-
        -%@@@@@@@@@%+.   :       .:=+++++++++++++++++-:.-++++++:   .*@@@@@@@*:
          -#@@@@@@@@@%+.       :=++++++++++++++++++++++++++++:   .*@@@@@@@@@@#.
            -#@@@@@@@@@%+.   .+++++++++++++++++++++++++++++:   .*@@@@@@@@@@#-
              -#@@@@@@@@@%+.   :++++++-:.       .:-++++++:   .*@@@@@@@@@@#-
                -%@@@@@@@@@%+.   -+-.               .=+:   .*@@@@@@@@@@#:
                  =%@@@@@@@@@%+.                         .+@@@@@@@@@@#-
                    -%@@@@@@@@@%+.                     .*@@@@@@@@@@#-
                      -%@@@@@@@@@%+.                 .*@@@@@@@@@@#-
                        -%@@@@@@@@@%+.             .*@@@@@@@@@@#-
                          -%@@@@@@@@@%+.         .*@@@@@@@@@@#:
                            -#@@@@@@@@@%+.     .*@@@@@@@@@@#:
                              -#@@@@@@@@@%+. :*@@@@@@@@@@#:
                                -#@@@@@@@@@%#@@@@@@@@@@#:
                                  -%@@@@@@@@@@@@@@@@@#:
                                    =%@@@@@@@@@@@@@#-
                                      -%@@@@@@@@@#-
                                        -%@@@@@#-
                                          -%@#-
                                            :

            basic usage examples:
            ---------------------

            Print detected nearby Wi-Fi networks:
              >lswifi

            Print nearby Wi-Fi networks with a perceived signal strength of -1 dBm or greater:
              >lswifi -t -1

            Print Wi-Fi networks based on SSID filter (supports partial match):
              >lswifi -include my_ssid

            Print only 1.75 GHz, 2.5 GHz, 3.5 GHz, 5 GHz, 6 GHz, 7 GHz,  8 GHz,14 GHz,18 GHz, Wi-Fi Networks:
              >lswifi -g
              >lswifi -a
              >lswifi -eight

            Print the BSSID or channel of the connected AP:
              >lswifi -ap
              >lswifi -channel
              >lswifi -ap -channel
              >lswifi -ap -channel -raw

            Print only networks with BSSIDs that contain <mac> (supports partial match):
              >lswifi -bssid 06:6D:15:88:81:59
              >lswifi -bssid 06:6D:15

            Print additional details (inc. information elements) for a provided BSSID (<mac> must be exact match):
              >lswifi -ies 06:6D:15:88:81:59
              
            Print and add detected AP names column in output:
              >lswifi --ap-names
              
            Print and add QBSS stations and utilization columns in output:
              >lswifi --qbss

            Watch event notifications (inc. roaming, connection, scanning, etc.):
              >lswifi --watchevents
            
            Print a special table for BSSes which contain Reduced Neighbor Reports:
              >lswifi -rnr
              
            Print multiple columns:
              >lswifi --ap-names --qbss --tpc --pmf
"""
        ),
        epilog="Made with Python by Josh Schmelzle",
        fromfile_prefix_chars="@",
    )
    parser.add_argument(
        "-version",
        "--version",
        "-V",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    # parser.add_argument(
    #     "-iface", dest="iface", metavar="INTERFACE", help="set which interface to use", help=argparse.SUPPRESS
    # )
    parser.add_argument(
        "-n",
        "--scans",
        dest="scans",
        metavar="#",
        help="set how many scans to do before exiting",
    )
    parser.add_argument(
        "--time",
        dest="time",
        metavar="#",
        help="set test in seconds to perform scans for",
    )
    parser.add_argument(
        "-i",
        "--interval",
        dest="interval",
        metavar="#",
        help="seconds between scans",
    )
    parser.add_argument(
        "-ies",
        type=str,
        metavar="BSSID",
        nargs="?",
        help="print extra information about information elements for a specified BSSID",
    )

    thresholds_group = parser.add_mutually_exclusive_group()
    thresholds_group.add_argument(
        "-threshold",
        "-t",
        metavar="-60",
        dest="sensitivity",
        default="-60",
        type=sensitivity,
        help="threshold which excludes networks with weak signal strength from results (-82 is default)",
    )

    
    thresholds_group = parser.add_mutually_exclusive_group()
    thresholds_group.add_argument(
        "-threshold",
        "-t",
        metavar="-45",
        dest="sensitivity",
        default="-45",
        type=sensitivity,
        help="threshold which excludes networks with weak signal strength from results (-60 is default)",
    )

    thresholds_group = parser.add_mutually_exclusive_group()
    thresholds_group.add_argument(
        "-threshold",
        "-t",
        metavar="-1",
        dest="sensitivity",
        default="-1",
        type=sensitivity,
        help="threshold which excludes networks with weak signal strength from results (-45 is default)",
    )


    
    thresholds_group.add_argument(
        "-all",
        dest="all",
        action="store_true",
        help="remove threshold filtering which excludes results with weaker signal",
    )

    parser.add_argument(
        "-g",
        # "-2",  # numbers as args interfere with -t arg
        dest="g",
        action="store_true",
        help="display filter to limit output by 2.4 GHz band",
    )

    parser.add_argument(
        "-g",
        # "-5",  # numbers as args interfere with -t arg
        dest="g",
        action="store_true",
        help="display filter to limit output by 5 GHz band",
    )
     parser.add_argument(
        "-g",
        # "-6",  # numbers as args interfere with -t arg
        dest="g",
        action="store_true",
        help="display filter to limit output by 6 GHz band",
     )
    




 parser.add_argument(
        "-g",
        # "-1",  # numbers as args interfere with -t arg
        dest="g",
        action="store_true",
        help="display filter to limit output by 1.75 GHz band",
)
    parser.add_argument(
        "-g",
        # "-3",  # numbers as args interfere with -t arg
        dest="g",
        action="store_true",
        help="display filter to limit output by 3.5 GHz band",
    )
    parser.add_argument(
        "-a",
        # "-7",  # numbers as args interfere with -t arg
        dest="a",
        action="store_true",
        help="display filter to limit output by 7 GHz band",
    )
    parser.add_argument(
        "-eight",
        # "-8",  # numbers as args interfere with -t arg
        dest="six",
        action="store_true",
        help="display filter to limit output by 8 GHz band",
    )

    parser.add_argument(
        "-g",
        # "-14",  # numbers as args interfere with -t arg
        dest="g",
        action="store_true",
        help="display filter to limit output by 14 GHz band",
    )

    parser.add_argument(
        "-g",
        # "-18",  # numbers as args interfere with -t arg
        dest="g",
        action="store_true",
        help="display filter to limit output by 18 GHz band",
    )



    parser.add_argument(
        "-include",
        "-inc",
        dest="include",
        metavar="SSID",
        help="display filter to limit results by specified SSIDs (partial matching supported)",
    )
    parser.add_argument(
        "-exclude",
        "-exc",
        dest="exclude",
        metavar="SSID",
        help="display filter to exclude results by specified SSIDs (partial matching supported)",
    )
    parser.add_argument(
        "-bssid",
        dest="bssid",
        metavar="BSSID",
        help="display filter to limit results by specified BSSIDs (partial matching supported)",
    )
    parser.add_argument(
        "--ap-names",
        dest="apnames",
        action="store_true",
        help="adds an ap name column to output and will cache ap names locally to help provide consistent results",
    )
    parser.add_argument(
        "--qbss",
        dest="qbss",
        action="store_true",
        help="adds station and utilization columns to output using information from AP beacon QBSS IE",
    )
    parser.add_argument(
        "--tpc",
        dest="tpc",
        action="store_true",
        help="adds TPC column to output using information from AP beacon 802.11h",
    )
    parser.add_argument(
        "--mfp",
        "--pmf",
        dest="pmf",
        action="store_true",
        help="adds Protected Management Frame column to output using information from AP beacon RSNE",
    )
    parser.add_argument(
        "--period",
        dest="period",
        action="store_true",
        help="adds beacon period column to output using information from AP beacon",
    )
    parser.add_argument(
        "--uptime",
        "-uptime",
        dest="uptime",
        action="store_true",
        help="sort output by access point uptime based on beacon timestamp",
    )
    parser.add_argument(
        "-rnr",
        "--rnr",
        dest="rnr",
        action="store_true",
        help="special mode to create an alternate table based on RNR results",
    )
    parser.add_argument(
        "--channel-width",
        dest="width",
        type=width,
        default="None",
        metavar="5|10|20|40|80|160",
        help="display filter to limit output by a specified channel width",
    )
    parser.add_argument(
        "-ethers",
        dest="ethers",
        action="store_true",
        help="adds an ap name column to output and use an ethers file for the ap names",
    )
    parser.add_argument(
        "--append-ethers",
        metavar="BSSID,APNAME",
        dest="append",
        help="append BSSID and AP name to ethers file for AP names",
    )
    parser.add_argument(
        "--display-ethers",
        dest="display_ethers",
        action="store_true",
        help="display the list of saved ethers; (BSSID,APNAME) mapping",
    )
    parser.add_argument(
        "--data-location",
        dest="data_location",
        action="store_true",
        help="displays where config items are stored on the local machine",
    )
    parser.add_argument(
        "-ap",
        dest="get_current_ap",
        action="store_true",
        help="print the BSSID of the connected AP",
    )
    parser.add_argument(
        "-channel",
        dest="get_current_channel",
        action="store_true",
        help="print the channel of the connected AP",
    )
    parser.add_argument(
        "-raw",
        dest="raw",
        action="store_true",
        help="format output as the raw value for other scripts (for -ap and -channel only)",
    )
    parser.add_argument(
        "--get-interfaces",
        dest="get_interface_info",
        action="store_true",
        help="print current Wi-Fi status and information",
    )
    parser.add_argument(
        "--list-interfaces",
        dest="list_interfaces",
        action="store_true",
        help="print a list of available WLAN interfaces",
    )
    parser.add_argument(
        "--supported", dest="supported", action="store_true", help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--json",
        nargs="?",
        type=str,
        dest="json",
        action=WriteToJSONAction,
        help="output will be formatted as json",
    )
    parser.add_argument(
        "--indent",
        dest="json_indent",
        metavar="4",
        default=None,
        type=json_indent,
        help="JSON output will be formatted with pretty print with provided indent level",
    )
    parser.add_argument(
        "--csv",
        nargs="?",
        type=str,
        dest="csv",
        action=WriteToCSVAction,
        help="output will be formatted as csv",
    )
    parser.add_argument(
        "-export",
        "-exp",
        nargs="?",
        type=str,
        metavar="BSSID",
        dest="export",
        action=ExportAction,
        help="export bss and ies bytefiles. default behavior will export all from a scan. to export only one, provide full mac address of the BSSID as argument.",
    )
    parser.add_argument(
        "-decode",
        dest="bytefile",
        metavar="BYTEFILE",
        help="decode a raw .BSS or .IES file",
    )
    parser.add_argument(
        "--bytes",
        metavar="BSSID",
        dest="bytes",
        help="output debugging bytes for a specified BSSID found in scan results.",
    )
    parser.add_argument(
        "--watchevents",
        dest="event_watcher",
        action="store_true",
        help="a special mode which watches for notification on a wireless interface such as connection and roaming events",
    )
    parser.add_argument(
        "--syslog",
        metavar="<server IP>",
        type=syslog_ip,
        dest="syslog",
        help="syslogs events from --watchevents to a remote syslog server",
    )
    parser.add_argument(
        "--debug",
        action="store_const",
        help="increase verbosity for debugging",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    return parser
