#!/usr/bin/env python
# encoding: utf-8

import codecs
import re
from os.path import dirname, join
from setuptools import setup


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
        raise RuntimeError(msg)
    return str(match.group('version'))


def read(*path_parts):
    """
    Get version module.

    :param tuple path_parts: path parts for version module.
    :return obj: module with version.
    """
    base_dir = dirname(__file__)
    file_path = join(base_dir, *path_parts)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='coindesk',
    version=find_version('coindesk', '__init__.py'),
    description='Bitcoin current and historical price',
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    author='Sergio de Diego',
    author_email='sergiodediego@outlook.com',
    url='https://github.com/sdediego/coindesk-api-client',
    download_url='https://github.com/sdediego/coindesk-api-client/archive/v1.1.0-alpha.tar.gz',
    packages=['coindesk'],
    install_requires=[
        "aiohttp>=3.6.1",
        "jsonschema>=3.0.2",
        "requests>=2.22.0",
        "furl>=2.1.0",
    ],
    license='MIT',
    keywords='api asynchronous Bitcoin blockchain client Coindesk Python',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
