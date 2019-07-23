# coding: utf-8

import argparse
import json
import os
from typing import NoReturn

from .android import get_android_lint_reports
from .gitdiff import GitDiff
from .ios import (convert_bracket_to_dot, get_ios_spell_check_reports,
                  get_swift_lint_reports, get_objective_c_warnings_reports)
from .svndiff import SvnDiff


def bracket_dot():
    parser = argparse.ArgumentParser()
    parser.add_argument('--last', action='store_true', default=False)
    parser.add_argument('--base', type=str, default=None)
    parser.add_argument('-w', '--whitespace', action='store_true', default=False)
    parser.add_argument('--all', action='store_true', default=False)
    arguments = parser.parse_args()

    ALL_MODE = arguments.all
    PICKUP_WHITESPACE_LINES = arguments.whitespace

    if ALL_MODE:
        target_lines = None
    else:
        git_diff = GitDiff()
        target_lines = git_diff.get_diff_lines(
            last_commit=arguments.last,
            base_hash=arguments.base,
            pickup_whitespace_lines=PICKUP_WHITESPACE_LINES)

    convert_bracket_to_dot(lines=target_lines)


def objc():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', type=str)
    parser.add_argument('--target', type=str)
    parser.add_argument('--config', type=str)
    parser.add_argument('--last', action='store_true', default=False)
    parser.add_argument('--base', type=str, default=None)
    parser.add_argument('--all', action='store_true', default=False)
    arguments = parser.parse_args()

    ALL_MODE = arguments.all

    if ALL_MODE:
        target_lines = None
    else:
        git_diff = GitDiff()
        target_lines = git_diff.get_diff_lines(
            last_commit=arguments.last,
            base_hash=arguments.base)

    reports = []

    objc_lint_reports = get_objective_c_warnings_reports(
        project=arguments.project,
        target=arguments.target,
        config=arguments.config,
        lines=target_lines)
    reports.extend(objc_lint_reports)

    _output_reports(reports)


def swift():
    parser = argparse.ArgumentParser()
    parser.add_argument('--last', action='store_true', default=False)
    parser.add_argument('--base', type=str, default=None)
    parser.add_argument('--all', action='store_true', default=False)
    arguments = parser.parse_args()

    ALL_MODE = arguments.all

    if ALL_MODE:
        target_lines = None
    else:
        git_diff = GitDiff()
        target_lines = git_diff.get_diff_lines(
            last_commit=arguments.last,
            base_hash=arguments.base)

    reports = []

    swift_spell_check_reports = get_ios_spell_check_reports(lines=target_lines)
    reports.extend(swift_spell_check_reports)

    swift_lint_reports = get_swift_lint_reports(lines=target_lines)
    reports.extend(swift_lint_reports)

    _output_reports(reports)


def android():
    parser = argparse.ArgumentParser()
    parser.add_argument('--last', action='store_true', default=False)
    parser.add_argument('--base', type=str, default=None)
    parser.add_argument('--all', action='store_true', default=False)
    parser.add_argument('--cache', action='store_true', default=False)
    parser.add_argument('--svn', action='store_true', default=False)
    arguments = parser.parse_args()

    ALL_MODE = arguments.all

    if ALL_MODE:
        target_lines = None
    else:
        if arguments.svn:
            svn_diff = SvnDiff()
            target_lines = svn_diff.get_diff_lines(
                base_rev=int(arguments.base))
        else:
            git_diff = GitDiff()
            target_lines = git_diff.get_diff_lines(
                last_commit=arguments.last,
                base_hash=arguments.base)

    reports = []

    lint_reports = get_android_lint_reports(
        lines=target_lines,
        use_cache=arguments.cache)
    reports.extend(lint_reports)

    _output_reports(reports)


def _output_reports(reports: list) -> NoReturn:
    current_dir = os.getcwd()
    OUTPUT_JSON_FILE = f'{current_dir}{os.sep}gitdiff_report.json'

    with open(OUTPUT_JSON_FILE, mode='w', encoding='utf-8') as f:
        json.dump(reports, f, indent=4, ensure_ascii=False)

    print(f'Successfully output in "{OUTPUT_JSON_FILE}""')
