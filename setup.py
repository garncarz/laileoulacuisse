#!/usr/bin/env python3

from DistUtilsExtra.auto import setup

classifiers = """\
Development Status :: 3 - Alpha
Environment :: X11 Applications :: GTK
Intended Audience :: End Users/Desktop
License :: OSI Approved :: GNU General Public License v2 (GPLv2)
Operating System :: POSIX :: Linux
Programming Language :: Python :: 3
Topic :: Internet :: WWW/HTTP :: Dynamic Content
"""

setup(
    name='laileoulacuisse',
    version='0.1.0',
    author='Ondřej Garncarz',
    author_email='ondrej@garncarz.cz',
    url='https://github.com/garncarz/laileoulacuisse',
    license='GPLv2',

    description="Restaurants' menu watcher tray app",
    keywords='restaurant food',
    classifiers=classifiers.splitlines(),
)
