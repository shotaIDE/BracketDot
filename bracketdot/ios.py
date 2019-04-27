# coding: utf-8

import re
from typing import NoReturn

from .gitdiff import GitDiff


def convert(base_hash: str = None) -> NoReturn:
    git_diff = GitDiff()
    results = git_diff.get_diff_lines(base_hash=base_hash)

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
