# coding: utf-8

import os
import re
import subprocess
from typing import NoReturn


def convert_bracket_to_dot(lines: dict) -> NoReturn:
    REPLACABLE_BRACKET_LINE = re.compile(
        r'(?!\A\s*'
        r'\[[a-zA-Z_][a-zA-Z0-9_.]*\s+[a-zA-Z_][a-zA-Z0-9_.]*\]'
        r'\s*;\s*\Z)'
        r'\A(.*)'
        r'\[([a-zA-Z_][a-zA-Z0-9_.]*)\s+([a-zA-Z_][a-zA-Z0-9_.]*)\]'
        r'(.*\s*)\Z')

    for target_file, line_numbers in lines.items():
        with open(file=target_file, mode='r', encoding='utf-8') as f:
            original_code = f.readlines()

        num_replaced = 0
        num_replaced_in_step = -1
        while num_replaced_in_step != 0:
            num_replaced_in_step = 0
            for i, line in enumerate(original_code):
                if i + 1 not in line_numbers:
                    continue

                matched = REPLACABLE_BRACKET_LINE.match(line)
                if not matched:
                    continue

                groups = matched.groups()
                replaced = f'{groups[0]}{groups[1]}.{groups[2]}{groups[3]}'
                original_code[i] = replaced
                num_replaced_in_step += 1
            num_replaced += num_replaced_in_step

        if num_replaced > 0:
            with open(file=target_file, mode='w', encoding='utf-8') as f:
                f.writelines(original_code)


def get_swift_lint_reports(lines: dict = None) -> list:
    LINT_OUTPUT_FORMAT = re.compile(
        r'^([^:]*):'
        r'([\d]+):([\d]+): '
        r'([\w]+): '
        r'(.*)$')

    ALL_MODE = lines is None

    if ALL_MODE:
        target_lines = {}
    else:
        target_lines = lines

    lint_cmd = 'swiftlint'
    result = subprocess.run(lint_cmd, check=False, capture_output=True).stdout

    lint_results_raw = result.decode('utf-8').split('\n')
    lint_results = [line.replace('\r', '') for line in lint_results_raw]

    current_dir = os.getcwd()
    issues = []

    for lint_result in lint_results:
        matched = LINT_OUTPUT_FORMAT.match(lint_result)
        if not matched:
            continue

        target_file_absolute_path = matched.groups()[0]
        target_file_relative_path = target_file_absolute_path.replace(
            current_dir, '')
        target_line = int(matched.groups()[1])
        target_column = int(matched.groups()[2])

        if (not ALL_MODE and
            (target_file_relative_path not in target_lines.keys() or
                target_line not in target_lines[target_file_relative_path])):
            continue

        severity = matched.groups()[3]
        message = matched.groups()[4]

        issues.append({
            'path': target_file_relative_path,
            'line': target_line,
            'column': target_column,
            'message': message,
            'tag': severity,
        })

    return issues
