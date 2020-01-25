# coding: utf-8

import glob
import os
import re
import subprocess
from typing import NoReturn

from .spell_check import spell_check


def convert_bracket_to_dot(lines: dict) -> NoReturn:
    REPLACABLE_BRACKET_LINE = re.compile(
        r'(?!\A\s*'
        r'\[[a-zA-Z_][a-zA-Z0-9_.]*\s+[a-zA-Z_][a-zA-Z0-9_.]*\]'
        r'\s*;\s*\Z)'
        r'\A(.*)'
        r'\[([a-zA-Z_][a-zA-Z0-9_.]*)\s+([a-zA-Z_][a-zA-Z0-9_.]*)\]'
        r'(.*\s*)\Z')

    BRACKET_SETTER_LINE = re.compile(
        r'\A(.*)'
        r'\[([a-zA-Z_][a-zA-Z0-9_.]*)\s+'
        r'set([A-Z])([a-zA-Z0-9_.]*):([a-zA-Z_][a-zA-Z0-9_.]*)\]'
        r'(.*\s*)\Z')

    BRACKET_GETTER_LINE = re.compile(
        r'\A(.*)'
        r'\[([a-zA-Z_][a-zA-Z0-9_.]*)\s+get([A-Z])([a-zA-Z0-9_.]*)\]'
        r'(.*\s*)\Z')

    BRACKET_INDEX_GET_LINE = re.compile(
        r'\A(.*)'
        r'\[([a-zA-Z_][a-zA-Z0-9_.]*)\s+'
        r'objectAtIndex:([a-zA-Z_][a-zA-Z0-9_.]*)\]'
        r'(.*\s*)\Z')

    BRACKET_INDEX_SET_LINE = re.compile(
        r'\A(.*)'
        r'\[([a-zA-Z_][a-zA-Z0-9_.]*)\s+'
        r'replaceObjectAtIndex:([a-zA-Z_][a-zA-Z0-9_.]*)\s+'
        r'withObject:([a-zA-Z_][a-zA-Z0-9_.]*)\]'
        r'(.*\s*)\Z')

    BRACKET_KEY_GET_LINE = re.compile(
        r'\A(.*)'
        r'\[([a-zA-Z_][a-zA-Z0-9_.]*)\s+'
        r'objectForKey:([a-zA-Z_][a-zA-Z0-9_.]*)\]'
        r'(.*\s*)\Z')

    BRACKET_KEY_SET_LINE = re.compile(
        r'\A(.*)'
        r'\[([a-zA-Z_][a-zA-Z0-9_.]*)\s+'
        r'setObject:([a-zA-Z_][a-zA-Z0-9_.]*)\s+'
        r'forKey:([a-zA-Z_][a-zA-Z0-9_.]*)\]'
        r'(.*\s*)\Z')

    for target_file, line_numbers in lines.items():
        with open(file=target_file,
                  mode='r',
                  encoding='utf-8',
                  errors='ignore') as f:
            original_code = f.readlines()

        num_replaced = 0
        num_replaced_in_step = -1
        while num_replaced_in_step != 0:
            num_replaced_in_step = 0
            for i, line in enumerate(original_code):
                if i + 1 not in line_numbers:
                    continue

                matched = REPLACABLE_BRACKET_LINE.match(line)
                if matched:
                    groups = matched.groups()
                    replaced = (
                        f'{groups[0]}'
                        f'{groups[1]}.{groups[2]}'
                        f'{groups[3]}')
                    original_code[i] = replaced
                    num_replaced_in_step += 1

                matched = BRACKET_SETTER_LINE.match(line)
                if matched:
                    groups = matched.groups()
                    replaced = (
                        f'{groups[0]}'
                        f'{groups[1]}.{groups[2].lower()}{groups[3]}'
                        f' = {groups[4]}'
                        f'{groups[5]}')
                    original_code[i] = replaced
                    num_replaced_in_step += 1

                matched = BRACKET_GETTER_LINE.match(line)
                if matched:
                    groups = matched.groups()
                    replaced = (
                        f'{groups[0]}'
                        f'{groups[1]}.{groups[2].lower()}{groups[3]}'
                        f'{groups[4]}')
                    original_code[i] = replaced
                    num_replaced_in_step += 1

                matched = BRACKET_INDEX_GET_LINE.match(line)
                if matched:
                    groups = matched.groups()
                    replaced = (
                        f'{groups[0]}'
                        f'{groups[1]}[{groups[2]}]'
                        f'{groups[3]}')
                    original_code[i] = replaced
                    num_replaced_in_step += 1

                matched = BRACKET_INDEX_SET_LINE.match(line)
                if matched:
                    groups = matched.groups()
                    replaced = (
                        f'{groups[0]}'
                        f'{groups[1]}[{groups[2]}]'
                        f' = {groups[3]}'
                        f'{groups[4]}')
                    original_code[i] = replaced
                    num_replaced_in_step += 1

                matched = BRACKET_KEY_GET_LINE.match(line)
                if matched:
                    groups = matched.groups()
                    replaced = (
                        f'{groups[0]}'
                        f'{groups[1]}[{groups[2]}]'
                        f'{groups[3]}')
                    original_code[i] = replaced
                    num_replaced_in_step += 1

                matched = BRACKET_KEY_SET_LINE.match(line)
                if matched:
                    groups = matched.groups()
                    replaced = (
                        f'{groups[0]}'
                        f'{groups[1]}[{groups[3]}]'
                        f' = {groups[2]}'
                        f'{groups[4]}')
                    original_code[i] = replaced
                    num_replaced_in_step += 1

            num_replaced += num_replaced_in_step

        if num_replaced > 0:
            with open(file=target_file, mode='w', encoding='utf-8') as f:
                f.writelines(original_code)


def get_objective_c_warnings_reports(project: str,
                                     target: str,
                                     config: str,
                                     lines: dict = None) -> list:
    ALL_MODE = lines is None

    if ALL_MODE:
        target_lines = {}
    else:
        target_lines = lines

    build_cmd = (
        'xcodebuild clean build '
        f'-project {project} '
        f'-target {target} '
        f'-config {config}')
    build_cmd_result = subprocess.Popen(
        build_cmd.split(), stdout=subprocess.PIPE)
    format_cmd = 'xcpretty'
    result = subprocess.run(
        format_cmd,
        check=False,
        capture_output=True,
        stdin=build_cmd_result.stdout).stdout

    build_results_raw = result.decode('utf-8').split('\n')
    build_results = [line.replace('\r', '') for line in build_results_raw]

    current_dir = os.getcwd()
    issues = []
    WARNING_OUTPUT_FORMAT = re.compile(
        r'^\S*\s+'
        r'([^:]*):'
        r'([\d]+):([\d]+): '
        r'(.*)$')

    for build_result in build_results:
        if not build_result.startswith('⚠️  '):
            continue

        matched = WARNING_OUTPUT_FORMAT.match(build_result)
        if not matched:
            continue

        target_file_absolute_path = matched.groups()[0]
        target_file_relative_path = target_file_absolute_path.replace(
            current_dir, '')[1:]
        target_line = int(matched.groups()[1])
        target_column = int(matched.groups()[2])

        if (not ALL_MODE and
            (target_file_relative_path not in target_lines.keys() or
                target_line not in target_lines[target_file_relative_path])):
            continue

        message = matched.groups()[3]

        issues.append({
            'path': target_file_relative_path,
            'line': target_line,
            'column': target_column,
            'message': message,
        })

    build_cmd_result = subprocess.Popen(
        build_cmd.split(), stdout=subprocess.PIPE)
    format_cmd = 'xcpretty -r json-compilation-database \
        --output compile_commands.json'
    subprocess.run(
        format_cmd.split(),
        check=False,
        capture_output=True,
        stdin=build_cmd_result.stdout)
    extract_cmd = 'oclint-json-compilation-database -- -report-type xcode'
    result = subprocess.run(
        extract_cmd.split(), check=False, capture_output=True).stdout

    lint_results_raw = result.decode('utf-8').split('\n')
    lint_results = [line.replace('\r', '') for line in lint_results_raw]

    LINT_OUTPUT_FORMAT = re.compile(
        r'^([^:]*):'
        r'([\d]+):([\d]+): '
        r'([^:]+): '
        r'([^\[]+)'
        r'\[([^|]+)|([^\]]+)\] '
        r'(.*)$')

    for lint_result in lint_results:
        matched = LINT_OUTPUT_FORMAT.match(lint_result)
        if not matched:
            continue

        target_file_absolute_path = matched.groups()[0]
        target_file_relative_path = target_file_absolute_path.replace(
            current_dir, '')[1:]
        target_line = int(matched.groups()[1])
        target_column = int(matched.groups()[2])

        if (not ALL_MODE and
            (target_file_relative_path not in target_lines.keys() or
                target_line not in target_lines[target_file_relative_path])):
            continue

        severity = matched.groups()[3]
        category = matched.groups()[4][:-1]
        id = matched.groups()[5]
        priority = matched.groups()[6]
        message = matched.groups()[7]

        issues.append({
            'path': target_file_relative_path,
            'line': target_line,
            'column': target_column,
            'message': message,
            'tag': f'[{severity}-{priority}] {category} / {id}',
        })

    print(f'Objective-C Lint: Found {len(issues)} issues.')

    return issues


def get_swift_lint_reports(parent_dir: str, lines: dict = None) -> list:
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

    directory_option = ''
    if parent_dir is not None:
        directory_option = f'--path {parent_dir}'

    lint_cmd = f'swiftlint {directory_option}'

    result = subprocess.run(
        lint_cmd.split(), check=False, capture_output=True).stdout

    lint_results_raw = result.decode('utf-8').split('\n')
    lint_results = [line.replace('\r', '') for line in lint_results_raw]

    if parent_dir is not None:
        current_dir = parent_dir
    else:
        current_dir = os.getcwd()
    issues = []

    for lint_result in lint_results:
        matched = LINT_OUTPUT_FORMAT.match(lint_result)
        if not matched:
            continue

        target_file_absolute_path = matched.groups()[0]
        target_file_relative_path = target_file_absolute_path.replace(
            current_dir, '')[1:]
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

    print(f'Swift lint: Found {len(issues)} issues.')

    return issues


def get_ios_spell_check_reports(parent_dir: str, lines: dict = None) -> list:
    ALL_MODE = lines is None

    if ALL_MODE:
        target_lines = {}
        swift_files = glob.glob('**/*.swift', recursive=True)
        for swift_file in swift_files:
            target_lines[swift_file] = []
    else:
        target_lines = lines

    HOME_DIR = os.environ['HOME']
    IGNORE_FILES = [
        '.gitdiffignore',
        f'{HOME_DIR}/.gitdiffignore',
    ]
    ignore_list_dup = []
    for ignore_file in IGNORE_FILES:
        if not os.path.exists(ignore_file):
            continue

        with open(ignore_file, mode='r', encoding='utf-8') as f:
            ignore_list_raw = f.readlines()
            ignore_list_dup += [
                word.replace('\n', '') for word in ignore_list_raw]
            print(f'Loaded {len(ignore_list_raw)} words \
                to ignore for spell check words \
                from {ignore_file}')

    ignore_list = list(set(ignore_list_dup))

    current_dir = os.getcwd()

    issues = []

    for target_file, line_numbers in target_lines.items():
        if parent_dir is not None:
            target_full_path = f'{parent_dir}/{target_file}'
        else:
            target_full_path = target_file

        with open(file=target_full_path,
                  mode='r',
                  encoding='utf-8',
                  errors='ignore') as f:
            original_code = f.readlines()

        for i, line in enumerate(original_code):
            if not ALL_MODE and i + 1 not in line_numbers:
                continue

            fixed_list = spell_check(line=line, ignore_list=ignore_list)

            if len(fixed_list) == 0:
                continue

            target_file_relative_path = target_file.replace(
                current_dir, '')
            target_line = i + 1

            for fixed in fixed_list:
                original_definition = fixed['src']
                fixed_definition = fixed['dst']
                message = (
                    f'In word \'{original_definition}\'. '
                    f'Did you mean \'{fixed_definition}\' ?')

                issues.append({
                    'path': target_file_relative_path,
                    'line': target_line,
                    'message': message,
                    'tag': 'Typo',
                })

    print(f'Swift spell checker: Found {len(issues)} issues.')

    return issues
