#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'requests',
    'sqlalchemy',
    'stockstats',
    'termcolor',
    'terminaltables'
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='cointrader',
    version='0.5.0',
    description="Cointrader is a trading application for crypto currencies.",
    long_description=readme + '\n\n' + history,
    author="Torsten Irländer",
    author_email='torsten.irlaender@googlemail.com',
    url='https://github.com/toirl/cointrader',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'cointrader=cointrader.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='cointrader coins crypto currency trading bot exchange poloniex bitcoin dash digital cash',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
