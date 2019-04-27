# coding: utf-8

import argparse

from .android import report
from .ios import convert


def ios():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=str, default='')
    parser.add_argument('--all', action='store_true', default=False)
    arguments = parser.parse_args()

    convert(
        base_hash=arguments.base)


def android():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=str, default='')
    parser.add_argument('--all', action='store_true', default=False)
    parser.add_argument('--cache', action='store_true', default=False)
    arguments = parser.parse_args()

    report(
        base_hash=arguments.base,
        all_mode=arguments.all,
        use_cache=arguments.cache)
