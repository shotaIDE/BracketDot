# coding: utf-8

import argparse
import json
import os
import sys
from typing import NoReturn

from .android import get_android_lint_reports, get_android_spell_check_reports
from .gitdiff import GitDiff
from .ios import (convert_bracket_to_dot, get_ios_spell_check_reports,
                  get_swift_lint_reports, get_objective_c_warnings_reports)
from .svndiff import SvnDiff


def bracket_dot():
    parser = argparse.ArgumentParser()
    parser.add_argument('--last', action='store_true', default=False)
    parser.add_argument('--base', type=str, default=None)
    parser.add_argument(
        '-w', '--ignore-whitespace', action='store_true', default=False)
    parser.add_argument('--all', action='store_true', default=False)
    arguments = parser.parse_args()

    ALL_MODE = arguments.all
    IGNORE_WHITESPACE_LINES = arguments.ignore_whitespace

    if ALL_MODE:
        target_lines = None
    else:
        git_diff = GitDiff()
        target_lines = git_diff.get_diff_lines(
            last_commit=arguments.last,
            base_hash=arguments.base,
            ignore_whitespace_lines=IGNORE_WHITESPACE_LINES)

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

    if not _is_contains_target_ext(target_lines.keys(), ['.m', '.mm']):
        print('No need to check '
              'because the difference of Objective-C was not found')
        return

    reports = []

    objc_lint_reports = get_objective_c_warnings_reports(
        project=arguments.project,
        target=arguments.target,
        config=arguments.config,
        lines=target_lines)
    reports.extend(objc_lint_reports)

    _output_reports(reports)

    is_objc_lint_error = len(objc_lint_reports) > 0
    exit_status = 1 if is_objc_lint_error else 0
    return sys.exit(exit_status)


def swift():
    parser = argparse.ArgumentParser()
    parser.add_argument('--last', action='store_true', default=False)
    parser.add_argument('--base', type=str, default=None)
    parser.add_argument('--all', action='store_true', default=False)
    arguments = parser.parse_args()

    REPOSITORY_PATH = _get_repository_path()

    ALL_MODE = arguments.all

    if ALL_MODE:
        target_lines = None
    else:
        git_diff = GitDiff()
        target_lines = git_diff.get_diff_lines(
            repository_path=REPOSITORY_PATH,
            last_commit=arguments.last,
            base_hash=arguments.base)

    if not _is_contains_target_ext(target_lines.keys(), ['.swift']):
        print('No need to check '
              'because the difference of Swift was not found')
        return

    reports = []

    swift_spell_check_reports = get_ios_spell_check_reports(
        parent_dir=REPOSITORY_PATH, lines=target_lines)
    reports.extend(swift_spell_check_reports)

    swift_lint_reports = get_swift_lint_reports(
        parent_dir=REPOSITORY_PATH, lines=target_lines)
    reports.extend(swift_lint_reports)

    _output_reports(reports)

    is_spell_check_error = len(swift_spell_check_reports) > 0
    is_swift_lint_error = len(swift_lint_reports) > 0
    exit_status = (1 if is_spell_check_error else 0) \
        | (2 if is_swift_lint_error else 0)
    return sys.exit(exit_status)


def android():
    parser = argparse.ArgumentParser()
    parser.add_argument('--last', action='store_true', default=False)
    parser.add_argument('--base', type=str, default=None)
    parser.add_argument('--all', action='store_true', default=False)
    parser.add_argument('--cache', action='store_true', default=False)
    parser.add_argument('--svn', action='store_true', default=False)
    parser.add_argument('--inspection', type=str, default=None)
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

    lint_reports = get_android_spell_check_reports(
        lines=target_lines,
        use_cache=arguments.cache,
        inspection=arguments.inspection)
    reports.extend(lint_reports)

    _output_reports(reports)


def _get_repository_path() -> str:
    return os.environ.get('BRACKET_DOT_TARGET_DIR_FOR_DEBUG')


def _output_reports(reports: list) -> NoReturn:
    current_dir = os.getcwd()
    OUTPUT_JSON_FILE = f'{current_dir}{os.sep}difflint_report.json'

    with open(OUTPUT_JSON_FILE, mode='w', encoding='utf-8') as f:
        json.dump(reports, f, indent=4, ensure_ascii=False)

    print(f'Successfully output in "{OUTPUT_JSON_FILE}""')


def _is_contains_target_ext(file_names: str, allowed_ext_list: list) -> bool:
    ext_list = [os.path.splitext(file_name)[1] for file_name in file_names]
    target_ext_list = [ext for ext in ext_list if ext in allowed_ext_list]
    return len(target_ext_list) > 0
