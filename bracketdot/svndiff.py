# coding: utf-8

import re
import subprocess


class SvnDiff():

    def __init__(self):
        pass

    def get_diff_lines(self, base_rev: int = None) -> dict:
        if base_rev is None:
            get_base_commit_cmd = 'svn log -l 10'
            result = subprocess.check_output(get_base_commit_cmd.split())
            commit_hash_raw_list = result.decode('utf-8').split('\n')
            base_commit_rev = commit_hash_raw_list[0].replace('"', '')
        else:
            base_commit_rev = base_rev

        head_commit_rev = 'HEAD'

        print(
            'Collecting diff between '
            f'{base_commit_rev} .. {head_commit_rev}')

        get_diff_cmd = (
            'svn diff -r '
            f'r{base_commit_rev}:{head_commit_rev}')
        result = subprocess.check_output(get_diff_cmd.split())

        diff_results_raw = result.decode('utf-8').split('\n')
        diff_results = [line.replace('\r', '') for line in diff_results_raw]

        RE_ADD_FILE_LINE = re.compile(r'^\+\+\+ ([\S]*).*$')
        BASE_NUMBER_LINE = re.compile(
            r'^@@ -[0-9]+(,[0-9]+)? \+([0-9]+)(,[0-9]+)? @@.*$')
        CODE_LINE = re.compile(r'^\+(.*)$')

        results = {}

        for line in diff_results:
            if line == '':
                continue

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

        return results
