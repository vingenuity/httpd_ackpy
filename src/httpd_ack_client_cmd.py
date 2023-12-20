#!/usr/bin/env python3

"""
Executes httpd-ack client operations from the command-line.
"""

import argparse
from httpd_ack.dumper import ConsoleDumper
from httpd_ack.parser import HttpdAckParser
import logging
from pathlib import Path
import sys
from typing import Dict, List
from urllib.error import URLError


_EXIT_CODES: Dict[str, int] = {
    'success': 0,
    'error_command': 1,
    'error_parser': 2,
    'error_file': 3,
    'error_server': 4,
    'error_downloader': 5
}


class Argument:
    """Simple class to contain argparse argument data for reuse."""
    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs


def execute_command_dump(server_url: str,
                         output_dir: Path,
                         dump_bios: bool = False,
                         dump_flash: bool = False,
                         dump_gdi: bool = False,
                         dump_page: bool = False,
                         dump_syscalls: bool = False,
                         dump_disc: bool = False,
                         tracks_to_dump: List[int] = []) -> int:
    """Executes the dump command with the given command-line arguments."""
    logging.info(f"Dumping Dreamcast data via httpd-ack server at '{server_url}'...")
    parser = HttpdAckParser()
    try:
        parser.parse_from_server(server_url)
        dumper = ConsoleDumper(
            parser.get_disc_data(),
            parser.get_dreamcast_data(),
            parser.get_server_url(),
            output_dir
        )
        dumper.dump_multiple(
            dump_bios,
            dump_flash,
            dump_gdi,
            dump_page,
            dump_syscalls,
            dump_disc,
            tracks_to_dump
        )
        return _EXIT_CODES['success']

    except URLError:
        logging.error(f"Unable to connect to httpd-ack server at '{server_url}'!")
        return _EXIT_CODES['error_server']


def execute_command_read(file: Path, server_url: str) -> int:
    """Executes the read command with the given command-line arguments."""
    parse_func_arg = None
    parse_func_name = None
    source_log_text = ""

    if file:
        parse_func_arg = file
        parse_func_name = "parse_from_file"
        source_log_text = f"file at '{file}'"

    if server_url:
        parse_func_arg = server_url
        parse_func_name = "parse_from_server"
        source_log_text = f"server at '{server_url}'"

    logging.info(f"Reading httpd-ack data from {source_log_text}...")
    parser = HttpdAckParser()
    try:
        parse_func = getattr(parser, parse_func_name)
        parse_func(parse_func_arg)
        logging.info("Disk Data:")
        logging.info(parser.get_disc_data())
        logging.info("\nDreamcast Data:")
        logging.info(parser.get_dreamcast_data())
        logging.info(f"\nServer version: {parser.get_server_version()}")
        return _EXIT_CODES['success']

    except AttributeError:
        logging.error(f"ERROR: Unable to find parser function {parse_func_name} on http-ack parser!")
        return _EXIT_CODES['error_parser']
    
    except FileNotFoundError:
        logging.error(f"ERROR: HTML file not found at '{file}'!")
        return _EXIT_CODES['error_file']
    
    except IsADirectoryError:
        logging.error(f"ERROR: HTML path '{file}' is to a directory, not a file!")
        return _EXIT_CODES['error_file']

    except URLError:
        logging.error(f"ERROR: Unable to connect to httpd-ack server at '{server_url}'!")
        return _EXIT_CODES['error_server']


def main(args: argparse.Namespace) -> int:
    """
    Contains the main functionality of this script.
    """
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    logging.basicConfig(level=logging.INFO,
                        handlers=[console_handler])
    
    # Remove func from args to prevent TypeError on call
    command_callable = args.func
    del args.func
    return command_callable(**vars(args))


def parse_arguments(arguments: List[str]) -> argparse.Namespace:
    """
    Parses command-line arguments into namespace data.
    """
    # The URL argument is used in both commands.
    # Thus, we reuse the argument data for consistency.
    url_arg = Argument(
        '--url',
        '-u',
        dest = 'server_url',
        type = str,
        help = 'URL for the httpd-ack server'
    )

    parser = argparse.ArgumentParser(
        description="Executes httpd-ack client operations from the command-line."
    )
    subparsers = parser.add_subparsers(help='httpd-ack operations to execute')

    parser_dump = subparsers.add_parser('dump', help='dump Dreamcast data via an httpd-ack server')
    parser_dump.set_defaults(func=execute_command_dump)
    parser_dump.add_argument(*url_arg.args, **url_arg.kwargs, required=True)
    parser_dump.add_argument('--output',
                        '-o',
                        dest='output_dir',
                        type=Path,
                        help="directory in which dumped files will be output")
    parser_dump.add_argument('--bios',
                        '-b',
                        dest='dump_bios',
                        action='store_true',
                        help="if set, the Dreamcast console's BIOS will be dumped")
    parser_dump.add_argument('--flash',
                        '-f',
                        dest='dump_flash',
                        action='store_true',
                        help="if set, the Dreamcast console's flash will be dumped")
    parser_dump.add_argument('--gdi',
                        '-g',
                        dest='dump_gdi',
                        action='store_true',
                        help="if set, the GDI of the Dreamcast disc will be dumped")
    parser_dump.add_argument('--page',
                        '-p',
                        dest='dump_page',
                        action='store_true',
                        help="if set, the HTML page from httpd-ack will be dumped")
    parser_dump.add_argument('--syscalls',
                        '-s',
                        dest='dump_syscalls',
                        action='store_true',
                        help="if set, the Dreamcast console's syscalls will be dumped")
    track_group = parser_dump.add_mutually_exclusive_group()
    track_group.add_argument('--disc',
                        '-d',
                        dest='dump_disc',
                        action='store_true',
                        help='if set, all tracks of the Dreamcast disc will be dumped')
    track_group.add_argument('--track',
                        '-t',
                        dest='tracks_to_dump',
                        type=List[int],
                        help='individual track(s) of the Dreamcast disc to dump')

    parser_read = subparsers.add_parser('read', help='read and display httpd-ack HTML')
    parser_read.set_defaults(func=execute_command_read)
    source_group = parser_read.add_mutually_exclusive_group(required=True)
    source_group.add_argument('--file',
                        '-f',
                        dest='file',
                        type=Path,
                        help='path to httpd-ack HTML file')
    source_group.add_argument(*url_arg.args, **url_arg.kwargs)

    return parser.parse_args(arguments)


if __name__ == "__main__":
    exit(main(parse_arguments(sys.argv[1:])))
