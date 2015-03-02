#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='laileoulacuisse',
    version='0.1',
    author='Ondřej Garncarz',
    author_email='ondrej@garncarz.cz',
    url='https://github.com/garncarz/laileoulacuisse',
    license='MIT',

    packages=['laileoulacuisse', 'laileoulacuisse.fetchers'],
    scripts=['bin/laileoulacuisse'],
)
