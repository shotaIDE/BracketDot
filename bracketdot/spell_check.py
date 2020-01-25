# coding: utf-8

import re

from spellchecker import SpellChecker

spell = SpellChecker()
DEFINITION_PATTERN = re.compile(
    r'(let|var|func|class|enum|struct)(\s+)([a-zA-Z0-9_]+)')
VARIABLE_PATTERN = re.compile(
    r'[a-zA-Z][a-z]*')


def spell_check(line: str, ignore_list: list = []) -> list:
    fixed_destination_list = []

    matched_definition_list = DEFINITION_PATTERN.findall(line)

    for matched_difinision in matched_definition_list:
        whole_definition = matched_difinision[2]

        words_in_definition_contains_upper = VARIABLE_PATTERN.findall(
            whole_definition)

        fixed_list = []

        for word in words_in_definition_contains_upper:
            word_lower = word.lower()

            if word_lower in ignore_list:
                continue

            misspelled = spell.unknown([word_lower])
            if not misspelled:
                continue

            fixed_word_lower = spell.correction(word)
            if (len(fixed_word_lower) >= 2 and
                    word[0].isupper()):
                fixed_word = (
                    fixed_word_lower[0].upper() +
                    fixed_word_lower[1:])
            else:
                fixed_word = fixed_word_lower

            fixed_list.append({
                'src': word,
                'dst': fixed_word,
            })

        if len(fixed_list) == 0:
            continue

        fixed_whole_definition = whole_definition
        for fixed in fixed_list:
            fixed_whole_definition = fixed_whole_definition.replace(
                fixed['src'], fixed['dst'])

        fixed_destination_list.append({
            'src': whole_definition,
            'dst': fixed_whole_definition,
        })

    return fixed_destination_list
