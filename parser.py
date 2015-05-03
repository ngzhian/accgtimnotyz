import subprocess
import unittest

import logging
logging.basicConfig(level=logging.DEBUG)


def get_var_names(fullpath):
    outputs = parse(fullpath)
    variables = list(get_var(outputs))
    logging.debug('variables: %s', variables)
    return variables

def parse(fullpath='test_snippet.js'):
    """Shell out to use the jar file and returns the output as an iterator"""
    # fullpath can be a glob too?
    output = subprocess.check_output(
        ['java', '-jar', 'compiler.jar', '--js_output_file', 'out.js', fullpath])
    # output = output.decode("utf-8", "strict").split('\n')
    output = output.decode(encoding='utf-8').split('\n')

    logging.debug('parsed output: %s', output)

    return map(str, filter(bool, output))

VAR_IDENTIFIER = 'VARNAME'

def get_var(lines):
    for line in lines:
        arr = line.split(' ')
        if len(arr) >= 3:
            if arr[0] == VAR_IDENTIFIER and arr[2]:
                yield arr[2]


class TestAnalyse(unittest.TestCase):
    def test_all(self):
        self.assertEqual(
            ['VARNAME NAME x 1 [source_file: test_snippet.js]',
             'VARNAME NAME y 2 [source_file: test_snippet.js] [is_constant_var: 1]'],
            list(parse()))


class TestGetVar(unittest.TestCase):
    def test_all(self):
        lines = ['VARNAME VAR x', 'VARNAME VAR y']
        variables = list(get_var(lines))
        self.assertEqual(['x', 'y'], variables)

if __name__ == '__main__':
    unittest.main()
