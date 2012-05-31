"""
:author: samu
:created: 5/16/12 5:05 PM
"""
import cmd
import os
import readline
import logging
import shlex


class CommandError(Exception): pass
class ValidationError(Exception): pass

try:
    ## Python 2.7
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        level=None
        def emit(self, record):
            pass

logger = logging.getLogger('sw_lib.managers.ocean_manager')
logger.addHandler(NullHandler()) # Prevent "no handler" warning


class CmdPlus(cmd.Cmd):
    history_file = None
    _history_storage = None

    def __init__(self, *args, **kwargs):
        cmd.Cmd.__init__(self, *args, **kwargs)
        self.history_load()

    def __del__(self):
        self.history_save()

    def history_save(self):
        if self.history_file is not None:
            readline.write_history_file(self.history_file)

    def history_load(self):
        if self.history_file is not None and os.path.exists(self.history_file):
            readline.read_history_file(self.history_file)

    def history_pause(self):
        """Store readline history to local history storage, and clear history"""
        self._history_storage = []
        for i in range(readline.get_current_history_length()):
            item = readline.get_history_item(i)
            if item is not None:
                self._history_storage.append(item)
        readline.clear_history()

    def history_resume(self):
        """Load readline history from local history storage"""
        readline.clear_history()
        if self._history_storage is not None:
            for item in self._history_storage:
                readline.add_history(item)

    @classmethod
    def _inline_input_choice(cls, message, choices):
        res = None
        while res not in choices:
            res = raw_input(message).strip()
        return res

    def emptyline(self):
        return

    def onecmd(self, line):
        """Interpret the argument as though it had been typed in response
        to the prompt.
        """
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line
        if cmd == '':
            return self.default(line)
        else:
            try:
                func = getattr(self, 'do_' + cmd)
            except AttributeError:
                return self.default(line, "Command not found")
            try:
                arg = shlex.split(arg)
 
