from __future__ import unicode_literals

import os
import ast

from prompt_toolkit.shortcuts import get_input
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import Completer, Completion


NOOP = {'arguments': [], 'commands': [], 'children': {}}


__version__ = '0.0.1'


def load_index(filename):
    with open(filename, 'r') as f:
        return ast.literal_eval(f.read())


class AWSCLICompleter(Completer):
    def __init__(self, index_data):
        self._index = index_data
        self._current = index_data['aws']
        self._last_position = 0
        self._last_completed_arg = None
        self._global_options = self._current['arguments']

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        word_before_cursor = text_before_cursor.split()[-1]
        self._last_position = len(document.text_before_cursor)
        if document.char_before_cursor == ' ':
            self._current = self._current['children'].get(
                word_before_cursor, NOOP)
            if word_before_cursor.startswith('--'):
                self._last_completed_arg = word_before_cursor[2:]

        for cmd in self._current['commands']:
            if cmd.startswith(word_before_cursor):
                #display_meta = self.meta_dict.get(a, '')
                display_meta = ''
                yield Completion(cmd, -len(word_before_cursor), display_meta=display_meta)
        for arg in self._current['arguments']:
            if arg.startswith(word_before_cursor):
                display_meta = ''
                yield Completion(arg, -len(word_before_cursor), display_meta=display_meta)
        for arg in self._global_options:
            if arg.startswith(word_before_cursor):
                display_meta = 'Documentation for %s YO YO' % arg
                yield Completion(arg, -len(word_before_cursor), display_meta=display_meta)


def main():
    if not os.path.isfile('completions.idx'):
        raise RuntimeError("Index file not created.  Please run "
                           "./build-index")
    index_data = load_index('completions.idx')
    completer = AWSCLICompleter(index_data)
    history = InMemoryHistory()
    while True:
        try:
            text = get_input('aws> ', completer=completer,
                             display_completions_in_columns=True)
        except KeyboardInterrupt:
            break
        else:
            print 'aws ' + text


if __name__ == '__main__':
    main()