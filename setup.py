#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="dircolor-editor",
    version="0.1.0",
    description="A GUI editor for .dircolors files",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    package_dir={"": "src"},
    install_requires=[
        "PyGObject>=3.42.0",
        "pycairo>=1.20.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "dircolor-editor=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Desktop Environment",
        "Topic :: Utilities",
    ],
)