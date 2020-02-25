# coding: utf-8

import re


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


def get_bracket_to_dot(line: str) -> dict:
    fixed_results = {}
    replaced_line = line
    num_replaced = 0

    while True:
        matched = REPLACABLE_BRACKET_LINE.match(replaced_line)
        if matched:
            groups = matched.groups()
            replaced = (
                f'{groups[0]}'
                f'{groups[1]}.{groups[2]}'
                f'{groups[3]}')
            replaced_line = replaced
            num_replaced += 1
            continue

        matched = BRACKET_SETTER_LINE.match(replaced_line)
        if matched:
            groups = matched.groups()
            replaced = (
                f'{groups[0]}'
                f'{groups[1]}.{groups[2].lower()}{groups[3]}'
                f' = {groups[4]}'
                f'{groups[5]}')
            replaced_line = replaced
            num_replaced += 1
            continue

        matched = BRACKET_GETTER_LINE.match(replaced_line)
        if matched:
            groups = matched.groups()
            replaced = (
                f'{groups[0]}'
                f'{groups[1]}.{groups[2].lower()}{groups[3]}'
                f'{groups[4]}')
            replaced_line = replaced
            num_replaced += 1
            continue

        matched = BRACKET_INDEX_GET_LINE.match(replaced_line)
        if matched:
            groups = matched.groups()
            replaced = (
                f'{groups[0]}'
                f'{groups[1]}[{groups[2]}]'
                f'{groups[3]}')
            replaced_line = replaced
            num_replaced += 1
            continue

        matched = BRACKET_INDEX_SET_LINE.match(replaced_line)
        if matched:
            groups = matched.groups()
            replaced = (
                f'{groups[0]}'
                f'{groups[1]}[{groups[2]}]'
                f' = {groups[3]}'
                f'{groups[4]}')
            replaced_line = replaced
            num_replaced += 1
            continue

        matched = BRACKET_KEY_GET_LINE.match(replaced_line)
        if matched:
            groups = matched.groups()
            replaced = (
                f'{groups[0]}'
                f'{groups[1]}[{groups[2]}]'
                f'{groups[3]}')
            replaced_line = replaced
            num_replaced += 1
            continue

        matched = BRACKET_KEY_SET_LINE.match(replaced_line)
        if matched:
            groups = matched.groups()
            replaced = (
                f'{groups[0]}'
                f'{groups[1]}[{groups[3]}]'
                f' = {groups[2]}'
                f'{groups[4]}')
            replaced_line = replaced
            num_replaced += 1
            continue

        break

    if num_replaced == 0:
        return

    fixed_results = {
        'src': line,
        'dst': replaced_line,
    }
    return fixed_results
