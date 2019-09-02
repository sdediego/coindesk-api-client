#!/usr/bin/env python
# encoding: utf-8

import codecs
import re

from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join
from setuptools import setup

# Custom logger for setup module
fileConfig(join(dirname(__file__), 'logging.cfg'))
logger = getLogger(__name__)


def read(*path_parts):
    """
    Get version module.

    :param tuple path_parts: path parts for version module.
    :return obj: module with version.
    """
    base_dir = dirname(__file__)
    file_path = join(base_dir, *path_parts)
    return codecs.open(file_path, encoding='utf-8').read()


def find_version(*path_parts):
    """
    Get current coindesk api client version.

    :param tuple path_parts: path parts for version module.
    :return str: api client version.
    """
    version = read(*path_parts)
    match = re.search(r'^__version__ = ["\'](?P<version>[^"\']*)["\']', version, re.M)
    if not match:
        msg = 'Unable to find module version.'
        logger.error(f'[find_version] Setup error. {msg}')
        raise RuntimeError(msg)
    return str(match.group('version'))


setup(
    name='coindesk',
    version=find_version('coindesk', '__init__.py'),
    description='Bitcoin current and historical price',
    long_description=read('README.md'),
    author='Sergio de Diego',
    url='https://github.com/sdediego/coindesk-api-client',
    packages=['coindesk'],
    install_requires=read('requirements.txt'),
    license='MIT',
    keywords='coindesk bitcoin blockchain api client Python',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Topic :: Office/Business :: Financial',
    ],
)
