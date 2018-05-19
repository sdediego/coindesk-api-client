#!/usr/bin/env python
# encoding: utf-8

import codecs
import re

from os.path import dirname, join
from setuptools import setup, find_packages


def read(*path_parts):
    file_path = join(dirname(__file__), *path_parts)
    return codecs.open(file_path, encoding='utf-8').read()


def find_version(*path_parts):
    version = read(*path_parts)
    match = re.search(r'^__version__ = ["\']([^"\']*)["\']', version, re.M)
    if match:
        return str(match.group(1))

    raise RuntimeError('Unable to find module version.')


setup(
    name='coindesk',
    verbose_name='CoinDesk API Client written in Python 3',
    packages=['coindesk'],
    author='Sergio de Diego',
    version=find_version('coindesk', '__init__.py'),
    description='Bitcoin current and historical price fetcher client',
    long_description=read('README.md'),
    url='https://github.com/sdediego/coindesk-api-client',
    license='MIT',
    requires=read('requirements.txt'),
    packages=find_packages(),
    keywords='CoinDesk API blockchain Bitcoin client Python',
    entry_points={
        'console_scripts': [
            'run_scheduler = scheduler',
        ],
    },
)
