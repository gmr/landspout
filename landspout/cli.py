# coding=utf-8
"""
Command Line Interface
======================

"""
import argparse
import logging
import os
from os import path
import sys

from landspout import core, __version__

LOGGER = logging.getLogger('landspout')
LOGGING_FORMAT = '[%(asctime)-15s] %(levelname)-8s %(name)-15s: %(message)s'


def exit_application(message=None, code=0):
    """Exit the application displaying the message to info or error based upon
    the exit code

    :param str message: The exit message
    :param int code: The exit code (default: 0)

    """
    log_method = LOGGER.error if code else LOGGER.info
    log_method(message.strip())
    sys.exit(code)


def parse_cli_arguments():
    """Return the base argument parser for CLI applications.


    :return: :class:`~argparse.ArgumentParser`

    """
    parser = argparse.ArgumentParser(
        'landspout', 'Static website generation tool',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        conflict_handler='resolve')

    parser.add_argument('-s', '--source', metavar='SOURCE',
                        help='Source content directory',
                        default='content')
    parser.add_argument('-d', '--destination', metavar='DEST',
                        help='Destination directory for built content',
                        default='build')
    parser.add_argument('-t', '--templates', metavar='TEMPLATE DIR',
                        help='Template directory',
                        default='templates')
    parser.add_argument('-b', '--base-uri-path', action='store', default='/')
    parser.add_argument('--whitespace', action='store',
                        choices=['all', 'single', 'oneline'],
                        default='all',
                        help='Compress whitespace')
    parser.add_argument('-n', '--namespace', type=argparse.FileType('r'),
                        help='Load a JSON file of values to inject into the '
                             'default rendering namespace.')
    parser.add_argument('-i', '--interval', type=int, default=3,
                        help='Interval in seconds between file '
                             'checks while watching or serving')
    parser.add_argument('--port', type=int, default=8080,
                        help='The port to listen on when serving')
    parser.add_argument('--debug', action='store_true',
                        help='Extra verbose debug logging')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {}'.format(__version__),
                        help='output version information, then exit')
    parser.add_argument('command', nargs='?',
                        choices=['build', 'watch', 'serve'],
                        help='The command to run', default='build')
    return parser.parse_args()


def validate_paths(args):
    """Ensure all of the configured paths actually exist."""
    if not path.exists(args.destination):
        LOGGER.warning('Destination path "%s" does not exist, creating',
                       args.destination)
        os.makedirs(path.normpath(args.destination))

    for file_path in [args.source, args.templates]:
        if not path.exists(file_path):
            exit_application('Path {} does not exist'.format(file_path), 1)


def main():
    """Application entry point"""
    args = parse_cli_arguments()
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format=LOGGING_FORMAT)
    LOGGER.info('Landspout v%s [%s]', __version__, args.command)
    validate_paths(args)
    landspout = core.Landspout(args)
    if args.command == 'build':
        landspout.build()
    elif args.command == 'watch':
        landspout.watch()
    elif args.command == 'serve':
        landspout.serve()
