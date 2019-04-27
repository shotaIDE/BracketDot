# coding: utf-8

from setuptools import setup

PACKAGE_NAME = 'bracketdot'
VERSION_NAME = '1.0'

setup(
    name=PACKAGE_NAME,
    version=VERSION_NAME,
    packages=[PACKAGE_NAME],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'bracket-dot=bracketdot.command_line:ios',
            'difflint-android=bracketdot.command_line:android',
        ],
    },
)
