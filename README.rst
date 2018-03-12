Landspout
=========
Landspout is a static website generation tool, using
`Tornado Template <http://www.tornadoweb.org/en/stable/template.html>`_. Create
your template structure, and your content, and point landspout at it.

|Version| |License|

Usage
-----
.. code::

   usage: Static website generation tool

   optional arguments:
     -h, --help            show this help message and exit
     -s SOURCE, --source SOURCE
                           Source content directory (default: content)
     -d DEST, --destination DEST
                           Destination directory for built content (default:
                           build)
     -t TEMPLATE DIR, --templates TEMPLATE DIR
                           Template directory (default: templates)
     -b BASE_URI_PATH, --base-uri-path BASE_URI_PATH
     --whitespace {all,single,oneline}
                           Compress whitespace (default: all)
     --debug               Extra verbose debug logging (default: False)
     -v, --version         output version information, then exit


.. |Version| image:: https://img.shields.io/pypi/v/landspout.svg?
   :target: https://pypi.org/project/landspout

.. |License| image:: https://img.shields.io/pypi/l/landspout.svg?
   :target: https://pypi.org/project/landspout
