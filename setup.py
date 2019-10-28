#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 17:45:08 2019

@author: dmitrii
"""

from setuptools import setup, find_packages
import os

packagename = 'data_proc'
version = '0.1'

with open(os.path.join('./', 'requirements.txt')) as f:
	install_requires = f.read().splitlines()

setup(
    name = packagename,
    version = version,
    license = 'GPLv3',
    author = 'Dmitrii Pushkarev',
    author_email='d-push@yandex.ru',
    description = 'A module with general functions for filamentation data processing',
    packages = find_packages(),
    install_requires = install_requires,
    keywords = 'science, filament, data processing',
)
