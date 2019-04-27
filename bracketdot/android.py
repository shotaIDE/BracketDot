# coding: utf-8

import json
import os
import subprocess
import xml.etree.ElementTree as ElementTree
from typing import NoReturn

from .gitdiff import GitDiff

DEFAULT_LINT_RESULTS_PATH = 'app/build/reports/lint-results.xml'


def report(base_hash: str = None, all_mode: bool = False,
           use_cache: bool = False) -> NoReturn:
    ALL_MODE = all_mode
    USE_CACHE = use_cache

    if ALL_MODE:
        results = {}
    else:
        git_diff = GitDiff()
        results = git_diff.get_diff_lines(base_hash=base_hash)

    if USE_CACHE:
        lint_report_file = DEFAULT_LINT_RESULTS_PATH
    else:
        android_lint_cmd = '.\\gradlew lint'
        result = subprocess.check_output(android_lint_cmd.split())
        result_list = result.decode('utf-8').split('\n')

        for line in result_list:
            if not line.startswith('Wrote XML report to file:///'):
                continue
            lint_report_file_raw = line[:28]
            lint_report_file = lint_report_file_raw.replace('/', os.sep)

        if lint_report_file is None:
            print('[ERROR] Lint report file was not found!')
            return

    lint_report_tree = ElementTree.parse(lint_report_file)
    lint_report_root = lint_report_tree.getroot()

    current_dir = os.getcwd()
    issues = []

    for issue in lint_report_root:
        if issue.tag != 'issue':
            continue

        location = issue.find('location')
        target_file_absolute_path = location.get('file')
        target_file_relative_path = target_file_absolute_path.replace(
            current_dir, '')
        target_line = int(location.get('line'))
        target_column = int(location.get('column'))

        if not ALL_MODE:
            if (target_file_relative_path not in results.keys() or
                    target_line not in results[target_file_relative_path]):
                continue

        message = issue.get('message')
        summary = issue.get('summary')
        explanation = issue.get('explanation')
        category = issue.get('category')
        id = issue.get('id')
        severity = issue.get('severity')
        priority = issue.get('priority')

        issues.append({
            'path': target_file_relative_path,
            'line': target_line,
            'column': target_column,
            'message': message,
            'summary': summary,
            'explanation': explanation,
            'tag': f'[{severity}-{priority}] {category} / {id}',
        })

    print(f'Found {len(issues)} issues.')

    OUTPUT_JSON_FILE = f'{current_dir}{os.sep}gitdiff_report.json'
    with open(OUTPUT_JSON_FILE, mode='w', encoding='utf-8') as f:
        json.dump(issues, f, indent=4)

    print(f'Successfully output in "{OUTPUT_JSON_FILE}""')
