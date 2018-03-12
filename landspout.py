# coding=utf-8
"""
Landspout is a static site generation tool.

"""
import argparse
import datetime
import logging
import os
from os import path
import sys

from tornado import template

__version__ = '0.1.0'

LOGGER = logging.getLogger(__name__)
LOGGING_FORMAT = '[%(asctime)-15s] %(levelname)-8s %(name)-15s: %(message)s'


class Landspout:
    """Static website build tool"""
    def __init__(self, args):
        self._base_path = args.base_uri_path
        self._source = path.abspath(args.source)
        self._dest = path.abspath(args.destination)
        self._loader = template.Loader(path.abspath(args.templates))
        self._whitespace = args.whitespace

    def build(self):
        """Primary action for building the static website."""
        LOGGER.info('Landspout v%s building to %r', __version__, self._dest)
        for root, dirs, files in os.walk(self._source):
            for filename in files:
                src_file = path.join(root, filename)
                dest_file = path.join(self._dest, filename)
                LOGGER.debug('Rendering %s', dest_file)

                info = os.stat(src_file)
                file_mtime = datetime.datetime.fromtimestamp(info.st_mtime)

                with open(src_file, 'r') as handle:
                    content = handle.read()

                renderer = template.Template(content, src_file, self._loader)

                with open(dest_file, 'wb') as handle:
                    try:
                        handle.write(
                            renderer.generate(
                                base_path=self.base_path,
                                filename=filename,
                                file_mtime=file_mtime,
                                static_url=self.static_url))
                    except Exception as err:
                        LOGGER.error('Error rendering %s: %r', dest_file, err)

    def base_path(self, filename):
        return '{}/{}'.format(self._base_path, filename)

    def static_url(self, filename):
        return self.base_path(filename)


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
    parser.add_argument('--debug', action='store_true',
                        help='Extra verbose debug logging')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {}'.format(__version__),
                        help='output version information, then exit')
    return parser.parse_args()


def validate_paths(args):
    """Ensure all of the configured paths actually exist."""
    for file_path in [args.source, args.destination, args.templates]:
        if not path.exists(file_path):
            exit_application('Path {} does not exist'.format(file_path), 1)


def main():
    """Application entry point"""
    args = parse_cli_arguments()
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format=LOGGING_FORMAT)
    validate_paths(args)
    Landspout(args).build()
