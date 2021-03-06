import shutil
import subprocess
import tempfile
import os

from cvise.passes.abstract import AbstractPass, BinaryState, PassResult

class LinesPass(AbstractPass):
    def check_prerequisites(self):
        return self.check_external_program("topformflat")

    def __format(self, test_case):
        tmp = os.path.dirname(test_case)
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, dir=tmp) as tmp_file:
            with open(test_case, "r") as in_file:
                try:
                    cmd = [self.external_programs["topformflat"], self.arg]
                    proc = subprocess.run(cmd, stdin=in_file, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                except subprocess.SubprocessError:
                    return (PassResult.ERROR, new_state)

            for l in proc.stdout.splitlines(keepends=True):
                if not l.isspace():
                    tmp_file.write(l)

        shutil.move(tmp_file.name, test_case)

    def __count_instances(self, test_case):
        with open(test_case, "r") as in_file:
            lines = in_file.readlines()
            return len(lines)

    def new(self, test_case):
        # None means no topformflat
        if self.arg != 'None':
            self.__format(test_case)
        instances = self.__count_instances(test_case)
        return BinaryState.create(instances)

    def advance(self, test_case, state):
        return state.advance()

    def advance_on_success(self, test_case, state):
        return state.advance_on_success(self.__count_instances(test_case))

    def transform(self, test_case, state, process_event_notifier):
        with open(test_case, "r") as in_file:
            data = in_file.readlines()

        old_len = len(data)
        data = data[0:state.index] + data[state.end():]
        assert len(data) < old_len

        tmp = os.path.dirname(test_case)
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, dir=tmp) as tmp_file:
            tmp_file.writelines(data)

        shutil.move(tmp_file.name, test_case)

        return (PassResult.OK, state)
