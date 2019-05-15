# coding: utf-8

import glob
import os
import re
import subprocess
from typing import NoReturn

from spellchecker import SpellChecker


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
        r'replaceObjectAtIndex:([a-zA-Z_][a-zA-Z0-9_.]*)'
        r'withObject:([a-zA-Z_][a-zA-Z0-9_.]*)\]'
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

            num_replaced += num_replaced_in_step

        if num_replaced > 0:
            with open(file=target_file, mode='w', encoding='utf-8') as f:
                f.writelines(original_code)


def get_objective_c_warnings_reports(project: str,
                                     target: str,
                                     config: str,
                                     lines: dict = None) -> list:
    LINT_OUTPUT_FORMAT = re.compile(
        r'^\S*\s+'
        r'([^:]*):'
        r'([\d]+):([\d]+): '
        r'(.*)$')

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
    build_result = subprocess.Popen(build_cmd.split(), stdout=subprocess.PIPE)
    format_cmd = 'xcpretty'
    result = subprocess.run(format_cmd, check=False, capture_output=True, stdin=build_result.stdout).stdout

    build_results_raw = result.decode('utf-8').split('\n')
    build_results = [line.replace('\r', '') for line in build_results_raw]

    current_dir = os.getcwd()
    issues = []

    for build_result in build_results:
        if not build_result.startswith('⚠️  '):
            continue

        matched = LINT_OUTPUT_FORMAT.match(build_result)
        if not matched:
            print(build_result)
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

    return issues


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

    return issues


def get_ios_spell_check_reports(lines: dict = None) -> list:
    DEFINITION_PATTERN = re.compile(
        r'(let|var|func|class|enum|struct)(\s+)([a-zA-Z0-9_]+)')
    VARIABLE_PATTERN = re.compile(
        r'[a-zA-Z][a-z]*')

    ALL_MODE = lines is None

    if ALL_MODE:
        target_lines = {}
        swift_files = glob.glob('**/*.swift', recursive=True)
        for swift_file in swift_files:
            target_lines[swift_file] = []
    else:
        target_lines = lines

    IGNORE_FILE = '.gitdiffignore'
    ignore_list = []
    if os.path.exists(IGNORE_FILE):
        with open(IGNORE_FILE, mode='r', encoding='utf-8') as f:
            ignore_list_raw = f.readlines()
            ignore_list = [
                word.replace('\n', '') for word in ignore_list_raw]

    current_dir = os.getcwd()
    spell = SpellChecker()
    issues = []

    for target_file, line_numbers in target_lines.items():
        with open(file=target_file, mode='r', encoding='utf-8') as f:
            original_code = f.readlines()

        for i, line in enumerate(original_code):
            if not ALL_MODE and i + 1 not in line_numbers:
                continue

            target_file_relative_path = target_file.replace(
                current_dir, '')
            target_line = i + 1

            matched_list = DEFINITION_PATTERN.findall(line)
            convert_list = []

            for matched in matched_list:
                definition_all = matched[2]

                variable_matched_list_raw = VARIABLE_PATTERN.findall(
                    definition_all)

                variable_matched_list = [
                    word
                    for word in variable_matched_list_raw
                    if word.lower() not in ignore_list]
                if variable_matched_list is None:
                    print(
                        f'[ERROR] "{definition_all}" is '
                        'not matched variable pattern.')

                for original_word in variable_matched_list:
                    misspelled = spell.unknown([original_word.lower()])
                    if not misspelled:
                        continue

                    correct_word_raw = spell.correction(original_word)
                    if (len(correct_word_raw) >= 2 and
                            original_word[0].isupper()):
                        correct_word = (
                            correct_word_raw[0].upper() +
                            correct_word_raw[1:-1])
                    else:
                        correct_word = correct_word_raw

                    convert_list.append({
                        'src': original_word,
                        'dst': correct_word,
                    })

            if len(convert_list) == 0:
                continue

            replaced_def = definition_all
            for convert in convert_list:
                replaced_def = replaced_def.replace(
                    convert['src'], convert['dst'])

            message = (
                f'In word \'{definition_all}\'. '
                f'Did you mean \'{replaced_def}\' ?')

            issues.append({
                'path': target_file_relative_path,
                'line': target_line,
                'message': message,
                'tag': 'Typo',
            })

    return issues
