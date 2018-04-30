# coding=utf-8
"""
Core Application
================

"""
import datetime
import json
import logging
import os
from os import path

from tornado import ioloop, template, web
import yaml

from landspout import modules

LOGGER = logging.getLogger('landspout')


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
        self._interval = args.interval
        self._namespace = self.load_namespace(args.namespace)
        self._loader = template.Loader(
            self._templates, namespace=self._namespace)
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
            'static_hash_cache': False,
            'static_handler_args': {
                'default_filename': 'index.html'
            },
            'static_url_prefix': '/'
        }
        app = web.Application([(r'/(.*)', web.StaticFileHandler)], **settings)
        app.listen(self._port)
        self._ioloop.call_later(self._interval, self.check_files)
        try:
            self._ioloop.start()
        except KeyboardInterrupt:
            self._ioloop.stop()

    def watch(self):
        """Watch the source and template directory for changes, triggering
        a render when files change.

        """
        LOGGER.info('Watching template and source directory for changes')
        self._ioloop.call_later(self._interval, self.check_files)
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
        self._ioloop.call_later(self._interval, self.check_files)

    def check_source(self):
        """Check the source directory looking for files to (re-)render,
        rendering them if required.

        """
        signatures = self.get_signatures(self._source)
        for fp, signature in signatures.items():
            if fp not in self._signatures['source'] or \
                    signature['stat'].st_mtime != \
                    self._signatures['source'][fp]['stat'].st_mtime:
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
        signatures = self.get_signatures(self._templates)
        for fp, signature in signatures.items():
            if fp not in self._signatures['templates'] or \
                    signature['stat'].st_mtime != \
                    self._signatures['templates'][fp]['stat'].st_mtime:
                render = True
                break
        if render:
            LOGGER.info('Template change detected, running full build')
            self._loader.reset()
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

    @staticmethod
    def load_namespace(namespace):
        """Load the namespace data in as JSON, returning the value as a dict.

        :rtype: dict

        """
        return json.load(namespace) if namespace else {}

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

        info = os.stat(source)
        file_mtime = datetime.datetime.fromtimestamp(info.st_mtime)

        with open(source, 'r') as handle:
            template_str = handle.read()

        content, data = None, None
        if source.endswith('.json'):
            content = json.loads(template_str)
        elif source.endswith('.yml') or source.endswith('.yaml'):
            content = yaml.load(template_str)

        if content:
            for var in ['template', 'data']:
                if var not in content:
                    LOGGER.error('%r not found in %s, skipping', var, source)
                    return
            template_str = content['template']
            data = content['data']
            extension = '.{}'.format(source.split('.')[:-1])
            dest = '{}.{}'.format(dest[:len(dest) - len(extension)],
                                  content.get('extension', 'html'))

        LOGGER.debug('Writing to %s', dest)
        try:
            renderer = template.Template(template_str, source, self._loader)
        except (SyntaxError, template.ParseError) as err:
            LOGGER.error('Error rendering %s: %r', dest, err)
            return False

        render_filename = filename if base_path == '.' \
            else '{}/{}'.format(base_path, filename)
        with open(dest, 'wb') as handle:
            try:
                handle.write(
                    renderer.generate(
                        base_path=self.base_path,
                        filename=render_filename,
                        file_mtime=file_mtime,
                        static_url=self.static_url,
                        data=data,
                        nested_data=modules.NestedData.render))
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
