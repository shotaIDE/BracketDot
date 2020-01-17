# coding: utf-8

import os
import subprocess
import xml.etree.ElementTree as ElementTree

DEFAULT_LINT_RESULTS_PATH = 'app/build/reports/lint-results.xml'


def get_android_lint_reports(lines: dict = None,
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
        android_lint_cmd = 'gradlew.bat lint'
        print(f'Running lint \"{android_lint_cmd}\" ...')

        result = subprocess.run(
            android_lint_cmd.split(),
            check=False,
            capture_output=True).stdout
        result_list = result.decode('utf-8').split('\n')

        for line in result_list:
            if not line.startswith('Wrote XML report to file:///'):
                continue
            lint_report_file_raw = line.replace(
                'Wrote XML report to file:///', '').replace('\r', '')
            lint_report_file = lint_report_file_raw.replace('/', os.sep)

        if not lint_report_file:
            print('[ERROR] Lint report file was not found!')
            return

    print(f'Load lint results from: {lint_report_file}')
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
            current_dir, '')[1:].replace(os.sep, '/')
        target_line_raw = location.get('line')
        target_column_raw = location.get('column')
        if target_line_raw is None or target_column_raw is None:
            continue
        target_line = int(target_line_raw)
        target_column = int(target_column_raw)

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

    print(f'Android lint: Found {len(issues)} issues.')

    return issues


def get_android_spell_check_reports(lines: dict = None,
                                    use_cache: bool = False,
                                    inspection: str = None) -> dict:
    SPELL_CHECK_RESULTS_PATH = 'inspection/SpellCheckingInspection.xml'

    ALL_MODE = lines is None
    USE_CACHE = use_cache

    if not USE_CACHE and inspection is None:
        print(f'Skipped spell check for missing inspection config option')
        return []

    INSPECTION_SETTINGS_PATH = inspection

    if ALL_MODE:
        target_lines = {}
    else:
        target_lines = lines

    if not USE_CACHE:
        android_inspection_cmd = (
            f'inspect.bat ./ {INSPECTION_SETTINGS_PATH} ./inspection')
        print(f'Running inspection \"{android_inspection_cmd}\" ...')

        subprocess.run(
            android_inspection_cmd.split(),
            check=False)

    print(f'Load lint results from: {SPELL_CHECK_RESULTS_PATH}')
    spell_check_report_tree = ElementTree.parse(SPELL_CHECK_RESULTS_PATH)
    spell_check_report_root = spell_check_report_tree.getroot()

    problems = []

    for problem in spell_check_report_root:
        if problem.tag != 'problem':
            continue

        target_file_absolute_path = problem.find('file').text
        target_file_relative_path = target_file_absolute_path.replace(
            'file://$PROJECT_DIR$/', '').replace(os.sep, '/')
        target_line_raw = problem.find('line').text
        if target_line_raw is None:
            continue
        target_line = int(target_line_raw)

        if (not ALL_MODE and
            (target_file_relative_path not in target_lines.keys() or
                target_line not in target_lines[target_file_relative_path])):
            continue

        message = problem.find('description').text
        severity = problem.find('problem_class').get('severity')
        category = problem.find('problem_class').get('attribute_key')

        problems.append({
            'path': target_file_relative_path,
            'line': target_line,
            'message': message,
            'tag': f'[{severity}] {category}',
        })

    print(f'Android spell check: Found {len(problems)} issues.')

    return problems
