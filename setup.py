# coding: utf-8

from setuptools import setup

PACKAGE_NAME = 'bracketdot'
VERSION_NAME = '1.0'

setup(
    name=PACKAGE_NAME,
    version=VERSION_NAME,
    packages=[PACKAGE_NAME],
    python_requires='>=3.6',
    install_requires=[
        'pyspellchecker>=0.4.0',
    ],
    extras_require={
        'dev': [
            'pytest-pycodestyle',
        ]
    },
    entry_points={
        'console_scripts': [
            'bracket-dot=bracketdot.command_line:bracket_dot',
            'difflint-objc=bracketdot.command_line:objc',
            'difflint-swift=bracketdot.command_line:swift',
            'difflint-android=bracketdot.command_line:android',
        ],
    },
)
