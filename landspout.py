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

from tornado import ioloop, template, web

__version__ = '0.2.0'

LOGGER = logging.getLogger(__name__)
LOGGING_FORMAT = '[%(asctime)-15s] %(levelname)-8s %(name)-15s: %(message)s'


class Landspout:
    """Static website build tool"""
    def __init__(self, args):
        self._args = args
        self._base_path = args.base_uri_path
        self._source = path.abspath(args.source)
        self._dest = path.abspath(args.destination)
        self._templates = path.abspath(args.templates)
        self._signatures = {
            'source': self.get_signatures(self._source),
            'templates': self.get_signatures(self._templates)
        }
        self._ioloop = ioloop.IOLoop.current()
        self._loader = template.Loader(self._templates)
        self._port = args.port
        self._whitespace = args.whitespace

    def build(self):
        """Primary action for building the static website."""
        LOGGER.debug('Building from %s', self._source)
        count = 0
        for root, dirs, files in os.walk(self._source):
            for filename in files:
                if self.render(path.relpath(root, self._source), filename):
                    count += 1
        LOGGER.info('Rendered %i files', count)

    def serve(self):
        """Run a HTTP server for serving the built content, while watching the
        source and template directory for changes, triggering a render when
        files change.

        """
        LOGGER.info('Serving on port %i from %s', self._port, self._dest)
        settings = {
            'autoreload': True,
            'static_path': self._dest,
            'static_handler_args': {
                'default_filename': 'index.html'
            },
            'static_url_prefix': '/'
        }
        app = web.Application([(r'/(.*)', web.StaticFileHandler)], **settings)
        app.listen(self._port)
        self._ioloop.add_timeout(1000, self.check_files)
        try:
            self._ioloop.start()
        except KeyboardInterrupt:
            self._ioloop.stop()

    def watch(self):
        """Watch the source and template directory for changes, triggering
        a render when files change.

        """
        LOGGER.info('Watching template and source directory for changes')
        self._ioloop.add_timeout(1000, self.check_files)
        try:
            self._ioloop.start()
        except KeyboardInterrupt:
            self._ioloop.stop()

    def base_path(self, filename):
        """Return the base path for the filename in the rendered website

        :param str filename: The file to render
        :return: str

        """
        return '{}{}'.format(self._base_path, filename)

    def check_files(self):
        """Check all of the files in both the source and template directories,
        looking for changes and then adding another call to this method on
        the IOLoop.

        """
        self.check_source()
        self.check_templates()
        self._ioloop.add_timeout(5000, self.check_files)

    def check_source(self):
        """Check the source directory looking for files to (re-)render,
        rendering them if required.

        """
        signatures = self.get_signatures(self._source)
        for fp, signature in signatures.items():
            if fp not in self._signatures['source'] or \
                    signature['stat'].st_mtime_ns != \
                    self._signatures['source'][fp]['stat'].st_mtime_ns:
                LOGGER.info('%s added or changed',
                            path.join(signature['base_path'],
                                      signature['filename']))
                self.render(
                    signature['base_path'], signatures[fp]['filename'])
        self._signatures['source'] = signatures

    def check_templates(self):
        """Check the template directory looking for changes. If changes are
        found, all files are rendered.

        """
        render = False
        signatures = self.get_signatures(self._source)
        for fp, signature in signatures.items():
            if fp not in self._signatures['templates'] or \
                    signature['stat'].st_mtime_ns != \
                    self._signatures['templates'][fp]['stat'].st_mtime_ns:
                render = True
                break
        if render:
            LOGGER.info('Template change detected, running full build')
            self.build()
            self._signatures['templates'] = signatures

    @staticmethod
    def get_signatures(dir_path):
        """Return all of the signatures for the files in the specified path.

        :param str dir_path: The path to traverse
        :rtype: dict

        """
        signatures = {}
        for root, dirs, files in os.walk(dir_path):
            for filename in files:
                file_path = path.join(root, filename)
                stat = os.stat(file_path)
                signatures[file_path] = {
                    'filename': filename,
                    'stat': stat,
                    'base_path': path.relpath(root, dir_path)}
        return signatures

    def render(self, base_path, filename):
        """Return the specified file.

        :param str base_path: The base path of the file to render
        :param str filename: The file to render

        """
        source = path.normpath(path.join(self._source, base_path, filename))
        dest = path.normpath(path.join(self._dest, base_path, filename))
        dest_path = path.dirname(dest)
        if not path.exists(dest_path):
            LOGGER.debug('Creating %s', dest_path)
            os.mkdir(dest_path)

        LOGGER.debug('Writing to %s', dest)
        info = os.stat(source)
        file_mtime = datetime.datetime.fromtimestamp(info.st_mtime)

        with open(source, 'r') as handle:
            content = handle.read()

        renderer = template.Template(content, source, self._loader)
        with open(dest, 'wb') as handle:
            try:
                handle.write(
                    renderer.generate(
                        base_path=self.base_path,
                        filename=filename if base_path == '.'
                            else '{}/{}'.format(base_path, filename),
                        file_mtime=file_mtime,
                        static_url=self.static_url))
            except Exception as err:
                LOGGER.error('Error rendering %s: %r', dest, err)
                return False
        return True

    def static_url(self, filename):
        """Return the static URL for the specified file.

        :param str filename: The file to return the static path for
        :return: str

        """
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
    parser.add_argument('-i', '--interval', type=int, default=5000,
                        help='Interval in milliseconds between file '
                             'checks when watching')
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
    for file_path in [args.source, args.destination, args.templates]:
        if not path.exists(file_path):
            exit_application('Path {} does not exist'.format(file_path), 1)


def main():
    """Application entry point"""
    args = parse_cli_arguments()
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format=LOGGING_FORMAT)
    validate_paths(args)
    LOGGER.info('Landspout v%s [%s]', __version__, args.command)
    landspout = Landspout(args)
    if args.command == 'build':
        landspout.build()
    elif args.command == 'watch':
        landspout.watch()
    elif args.command == 'serve':
        landspout.serve()
