#!/usr/local/bin/python3
import os
import sys

from setuptools import setup, find_packages

sys.path.insert(0, os.path.abspath("."))
from vfxClientToolkit import (
    __title__,
    __author__,
    __author_email__,
    __description__,
    __url__,
    __license__,
)
from vfxClientToolkit._version import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


requirements = [
    "requests",
    "black",
    "mypy",
    "isort",
    "pipenv",
    "progress",
    "gspread",
    "requests",
    "pillow",
    "qtmodern",
    "pyside2",
    "python-pushover",
    "pyyaml",
    "mailer",
    "pandas",
    "xlsxwriter",
    "json2html",
    "dropbox",
    "prompt_toolkit",
    "virtualenv",
]

setup(
    name=__title__,
    include_package_data=True,
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    description=__description__,
    license=__license__,
    url=__url__,
    dependency_links=[
        "https://github.com/shotgunsoftware/python-api/tarball/master#egg=package=3.2.2",
        "https://github.com/michaeljones/sphinx-to-github.git#egg=sphinx-to-github",
    ],
    scripts=[
        "scripts/noteBao",
        "scripts/mrFilmOut",
        "scripts/ingestIt",
        "scripts/reports",
        "scripts/mailIt",
        "scripts/fml",
        "scripts/vfxTray",
        "scripts/vfxConfigManager",
    ],
    packages=find_packages(),
    long_description=read("README.md"),
    install_requires=requirements,
    classifiers=["License :: OSI Approved :: MIT License"],
)
