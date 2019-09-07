#!/usr/bin/env python
# encoding: utf-8

import codecs
import re

from setuptools import setup

from coindesk import utils


setup(
    name='coindesk',
    version=utils.find_version('coindesk', '__init__.py'),
    description='Bitcoin current and historical price',
    long_description=utils.read('README.md'),
    author='Sergio de Diego',
    url='https://github.com/sdediego/coindesk-api-client',
    packages=['coindesk'],
    install_requires=utils.read('requirements.txt'),
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
