# coding: utf-8

import os
import subprocess
import xml.etree.ElementTree as ElementTree

DEFAULT_LINT_RESULTS_PATH = 'app/build/reports/lint-results.xml'


def get_android_lint_reports(lines: str = None,
                             use_cache: bool = False) -> dict:
    ALL_MODE = lines is None
    USE_CACHE = use_cache

    if ALL_MODE:
        target_lines = {}
    else:
        target_lines = lines

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

        if (not ALL_MODE and
            (target_file_relative_path not in target_lines.keys() or
                target_line not in target_lines[target_file_relative_path])):
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

    return issues
