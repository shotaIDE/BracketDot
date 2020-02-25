# coding: utf-8

import pkg_resources

if __name__ == "__main__":
    console_script = pkg_resources.load_entry_point(
        'bracketdot', 'console_scripts', 'bracket-dot')
    console_script()
