#!/usr/bin/env python3

from setuptools import setup, find_namespace_packages
from pathlib import Path


setup(
    name="ean",
    version="0.0.2",
    description="ean is a python module to create EAN13 (ISBN) .svg barcode",
    author="Timur U",
    author_email="ucomru@pm.me",
    url="https://github.com/ucomru/python-ean",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(where="src"),
    package_dir={"": "src"},
    license="MIT",
    install_requires=[
        "lxml",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="barcode ean ean13 isbn svg",
    python_requires='>=3.8'
)
