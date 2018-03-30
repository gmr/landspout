# coding=utf-8
from setuptools import setup

setup(name='landspout',
      version='0.2.1',
      description='Static website generation tool',
      long_description=open('README.rst').read(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: BSD License'
      ],
      keywords='static website generation',
      author='Gavin M. Roy',
      author_email='gavinmroy@gmail.com',
      url='https://github.com/gmr/landspout',
      license='BSD',
      py_modules=['landspout'],
      package_data={'': ['LICENSE', 'README.rst']},
      include_package_data=True,
      install_requires=[
          'tornado'
      ],
      entry_points=dict(console_scripts=['landspout=landspout:main']),
      zip_safe=True)
