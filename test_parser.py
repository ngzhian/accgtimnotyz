import unittest

from parser import get_var, parse


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
