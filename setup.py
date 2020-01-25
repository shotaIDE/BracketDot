# coding: utf-8

from setuptools import setup

description = ('A tool that runs lint '
               'focusing only on the latest changes in Git.')

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='bracketdot',
    version='1.0.0',
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/shotaIDE/BracketDot',
    author='Shota Ide',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='development lint git',
    packages=['bracketdot'],
    install_requires=[
        'pyspellchecker>=0.4.0',
    ],
    python_requires='~=3.6',
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
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
