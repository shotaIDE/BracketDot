# coding: utf-8

import argparse
import json
import os
from typing import NoReturn

from .android import get_android_lint_reports
from .gitdiff import GitDiff
from .ios import convert_bracket_to_dot, get_swift_lint_reports


def ios():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=str, default='')
    parser.add_argument('--all', action='store_true', default=False)
    arguments = parser.parse_args()

    ALL_MODE = arguments.all

    if ALL_MODE:
        target_lines = None
    else:
        git_diff = GitDiff()
        target_lines = git_diff.get_diff_lines(base_hash=arguments.base)

    reports = []

    # convert_bracket_to_dot(lines=target_lines)

    swift_lint_reports = get_swift_lint_reports(lines=target_lines)
    reports.extend(swift_lint_reports)

    _output_reports(reports)


def android():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=str, default='')
    parser.add_argument('--all', action='store_true', default=False)
    parser.add_argument('--cache', action='store_true', default=False)
    arguments = parser.parse_args()

    ALL_MODE = arguments.all

    if ALL_MODE:
        target_lines = None
    else:
        git_diff = GitDiff()
        target_lines = git_diff.get_diff_lines(base_hash=arguments.base)

    reports = []

    lint_reports = get_android_lint_reports(
        lines=target_lines,
        use_cache=arguments.cache)
    reports.extend(lint_reports)


def _output_reports(reports: list) -> NoReturn:
    current_dir = os.getcwd()
    OUTPUT_JSON_FILE = f'{current_dir}{os.sep}gitdiff_report.json'

    with open(OUTPUT_JSON_FILE, mode='w', encoding='utf-8') as f:
        json.dump(reports, f, indent=4)

    print(f'Successfully output in "{OUTPUT_JSON_FILE}""')
