#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup, find_packages


setup(
    name='coindesk-api-client',
    version='1.0',
    description='CoinDesk API Client module',
    author='Sergio de Diego',
    url='https://github.com/sdediego/coindesk-api-client',
    license='MIT',
    packages=find_packages(),
    keywords='CoinDesk API client Python',
    entry_points={
        'console_scripts': [
            'run_scheduler = scheduler',
        ],
    },
)
