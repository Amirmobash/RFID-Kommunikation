#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup script for the pi-rc522 library.
Author: Amir Mobasheraghdam
Date: 2025
"""

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


def get_version():
    """
    Retrieve the version number from pirc522/version.py.
    If the file is missing or malformed, fall back to a default.
    """
    version_file = os.path.join(os.path.dirname(__file__), 'pirc522', 'version.py')
    try:
        with open(version_file, 'r') as f:
            for line in f:
                if line.startswith('__version__'):
                    # Extract the version string
                    version = line.split('=')[1].strip().strip('"').strip("'")
                    return version
    except (IOError, IndexError):
        pass
    # Fallback version (should not happen in a proper release)
    return '0.0.0'


class PyTest(TestCommand):
    """
    Custom test command that runs pytest.
    """
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Import pytest here to avoid requiring it for installation
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


# Read the long description from README.md (if present)
try:
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = 'Raspberry Pi Python library for the SPI RFID RC522 module.'


setup(
    name='pi-rc522',
    version=get_version(),
    description='Raspberry Pi Python library for the SPI RFID RC522 module',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Amir Mobasheraghdam',
    author_email='your-email@example.com',   # Replace with actual email if desired
    url='https://github.com/amirmoba/pi-rc522',
    license='MIT',
    packages=find_packages(exclude=['tests', 'docs']),
    include_package_data=True,
    install_requires=[
        'spidev',           # SPI communication
        'RPi.GPIO',         # GPIO control on Raspberry Pi
    ],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Topic :: System :: Hardware',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='raspberry pi rfid rc522 spi',
    project_urls={
        'Source': 'https://github.com/amirmoba/pi-rc522',
        'Tracker': 'https://github.com/amirmoba/pi-rc522/issues',
    },
)
