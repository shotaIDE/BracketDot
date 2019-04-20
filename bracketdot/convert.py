# coding: utf-8

import re
import subprocess


def convert():
    get_base_commit_cmd = 'git log --pretty=format:"%P"'
    result = subprocess.check_output(get_base_commit_cmd.split())
    base_commit_hash = result.decode('utf-8').split('\n')[0].replace('"', '')

    head_commit_hash = 'HEAD'

    get_diff_cmd = (
        'git --no-pager diff '
        f'{base_commit_hash}..{head_commit_hash} -w -U0')
    result = subprocess.check_output(get_diff_cmd.split())
    diff_results_raw = result.decode('utf-8').split('\n')
    diff_results = [line.replace('\r', '') for line in diff_results_raw]

    RE_ADD_FILE_LINE = re.compile(r'^\+\+\+ b/(.*)$')
    BASE_NUMBER_LINE = re.compile(
        r'^@@ -[0-9]+(,[0-9]+)? \+([0-9]+)(,[0-9]+)? @@.*$')
    CODE_LINE = re.compile(r'^\+(.*)$')

    results = {}

    for line in diff_results:
        if line.startswith('---'):
            continue

        matched = RE_ADD_FILE_LINE.match(line)
        if matched:
            target_file = matched.groups()[0]
            results[target_file] = []
            continue

        matched = BASE_NUMBER_LINE.match(line)
        if matched:
            target_line = int(matched.groups()[1])
            continue

        matched = CODE_LINE.match(line)
        if matched:
            results[target_file].append(target_line)
            target_line += 1
            continue

    REPLACABLE_BRACKET_LINE = re.compile(
        r'(?!\A\s*'
        r'\[[a-zA-Z_][a-zA-Z0-9_.]*\s+[a-zA-Z_][a-zA-Z0-9_.]*\]'
        r'\s*;\s*\Z)'
        r'\A(.*)'
        r'\[([a-zA-Z_][a-zA-Z0-9_.]*)\s+([a-zA-Z_][a-zA-Z0-9_.]*)\]'
        r'(.*\s*)\Z')

    for target_file, line_numbers in results.items():
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
