import unittest
from analyse import CasingEngine, VerbosityEngine, PrefixEngine, SubsequenceEngine, analyse

class TestCasingEngine(unittest.TestCase):
    def test_camel(self):
        ce = CasingEngine(['camelCase', 'everyThing'])
        result = ce.analyse()
        self.assertEqual(result.attribute, 'camelCase')

    def test_under(self):
        ce = CasingEngine(['under_score', 'every_thing'])
        result = ce.analyse()
        self.assertEqual(result.attribute, 'under_score')

    def test_under(self):
        ce = CasingEngine(['neutral', 'basic'])
        result = ce.analyse()
        self.assertEqual(result.attribute, 'neutral')


class TestVerbosityEngine(unittest.TestCase):
    def test_concise(self):
        engine = VerbosityEngine(['s', 'h', 'o', 'r', 't', 'is', 'sweet'])
        result = engine.analyse()
        self.assertEqual(result.attribute, 'concise')

    def test_verbose(self):
        engine = VerbosityEngine(['iLikeLongName', 'thisSweetVariable', 'sweet'])
        result = engine.analyse()
        self.assertEqual(result.attribute, 'verbose')


class TestPrefixEngine(unittest.TestCase):
    def test_prefixes(self):
        engine = PrefixEngine(['asdf', 'asbf', 'asbc'])
        result = engine.analyse()
        self.assertEqual(result.attribute, 'as')


class TestSubsequenceEngine(unittest.TestCase):
    def test_subsequence(self):
        engine = SubsequenceEngine(['is_bool', 'is_great', 'this_is_fun'])
        result = engine.analyse()
        self.assertEqual(result.attribute, 'is')


class TestAnalyse(unittest.TestCase):
    def test_all(self):
        variables = ['asdf', 'hijkl']
        results = analyse(variables)
        self.assertEqual(
            results['highlights']['longest'], {'hijkl': 5})
        self.assertEqual(
            results['stats']['longest_10'],
            [{'hijkl': 5}, {'asdf': 4}])

if __name__ == '__main__':
    unittest.main()
