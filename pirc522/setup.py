#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


def get_version():
    with open('pirc522/version.py', 'r') as version_file:
        for line in version_file:
            if line.startswith('__version__'):
                version = line.split('=')[1].strip().strip('"')
                return version


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name='pi-rc522',
    packages=find_packages(),
    include_package_data=True,
    version=get_version(),
    description='Raspberry Pi Python Bibliothek für das SPI RFID RC522 Modul',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
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
    ],
    keywords='raspberry pi rfid rc522 spi',
    author='Amir Mobasheraghdam',
    author_email='your-email@example.com',
    url='https://github.com/amirmoba/pi-rc522',
    license='MIT',
    install_requires=['spidev', 'RPi.GPIO'],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    python_requires='>=3.5',
)
