# coding=utf-8
import setuptools

from landspout import __version__


setuptools.setup(
    name='landspout',
    version=__version__,
    description='Static website generation tool',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: BSD License'
    ],
    keywords='static website generation',
    author='Gavin M. Roy',
    author_email='gavinmroy@gmail.com',
    url='https://github.com/gmr/landspout',
    license='BSD',
    packages=['landspout'],
    package_data={'': ['LICENSE', 'README.rst']},
    include_package_data=True,
    install_requires=[
        'pyyaml',
        'tornado'
    ],
    entry_points=dict(console_scripts=['landspout=landspout.cli:main']),
    zip_safe=True)
