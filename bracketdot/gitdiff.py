# coding: utf-8

import os
import re
import subprocess


class GitDiff():

    def __init__(self):
        pass

    def get_diff_lines(self,
                       repository_path: str = None,
                       last_commit: bool = False,
                       base_hash: str = None,
                       ignore_whitespace_lines: bool = False) -> dict:
        current_changed = not last_commit and (base_hash is None)

        if last_commit:
            get_base_commit_cmd = 'git log --pretty=format:"%p"'
            result = subprocess.check_output(get_base_commit_cmd.split())
            commit_hash_raw_list = result.decode('utf-8').split('\n')
            last_commit_hash_raw = commit_hash_raw_list[0].replace('"', '')
            base_commit_hash = last_commit_hash_raw.split()[0]

            print(f'Extracted the last change: {base_commit_hash} .. HEAD')
        else:
            base_commit_hash = base_hash

        head_commit_hash = 'HEAD'

        directory_option = ''
        if repository_path is not None:
            directory_option = f'-C {repository_path} '

        if current_changed:
            get_diff_cmd = (
                'git '
                f'{directory_option}'
                '--no-pager diff '
                '--staged '
                f'{"-w " if ignore_whitespace_lines else ""}'
                '-U0')
        else:
            get_diff_cmd = (
                'git '
                f'{directory_option}'
                '--no-pager diff '
                f'{base_commit_hash} {head_commit_hash} '
                f'{"-w " if ignore_whitespace_lines else ""}'
                '-U0')

        print(f'Collecting diff \"{get_diff_cmd}\" ...')

        result = subprocess.check_output(get_diff_cmd.split())

        diff_results_raw = result.decode('utf-8', 'ignore').split('\n')
        diff_results = [line.replace('\r', '') for line in diff_results_raw]

        RE_ADD_FILE_LINE = re.compile(r'^\+\+\+ b/(.*)$')
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
                target_file_raw = matched.groups()[0]
                target_file = target_file_raw.replace('\t', '')
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

        for target_file, target_lines in results.items():
            print(f'  found {len(target_lines)} diff lines in {target_file}')

        return results
