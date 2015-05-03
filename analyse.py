from collections import Counter
import pandas as pd
import re

import logging
logging.basicConfig(level=logging.DEBUG)
"""
Engines available:

    class VerbosityEngine():
    class CasingEngine():
    class PrefixEngine():
    class SubsequenceEngine():
"""

def analyse(variables):
    """
    Variables is just a list of variable names.

    returns:
     {
         'highlights': {
             'longest': {'var1': 4},
             'most_used': {'var2': 4}
         },
         'stats': {
             'longest_10': [{'var1': 4}, {'var2': 4}],
             'most_used_10': [{'var2': 4}, {'var1': 4}]
         },
         'raw': {
             'length':
                {
                    'var1': 3
                    'var2': 3
                }
             'usage':
                {
                    'var1': 2
                    'var2': 3
                }
         }
      }
    """
    logging.debug('variables: %s', variables)
    if not variables:
        return None
    s = pd.Series(variables)
    df = pd.DataFrame(s.tolist(), index=s, columns=['name'])
    df['count'] = 1

    # gets the length of each variable
    df['length'] = df['name'].map(len)
    length = df.groupby('name').max()['length']

    longest_10 = length.order(ascending=False)[:10]
    longest = longest_10[:1]

    # count how many times each variable is used
    usage = df.groupby('name').sum()['count']
    most_used_10 = usage.order(ascending=False)[:10]
    most_used = most_used_10[:1]

    highlights = {
        'longest': longest.to_dict(),
        'most_used': most_used.to_dict(),
    }
    stats = {
        'longest_10': to_list_of_dicts(longest_10),
        'most_used_10': to_list_of_dicts(most_used_10),
    }
    raw = {
        'length': length.to_dict(),
        'usage': usage.to_dict(),
    }


    engines = [
        VerbosityEngine,
        CasingEngine,
        PrefixEngine,
        SubsequenceEngine]

    analysis = {}
    for engine in engines:
        e = engine(variables)
        result = e.analyse()
        analysis[e.name] = result.to_dict()
    results = dict(
        stats=stats,
        highlights=highlights,
        raw=raw,
        analysis=analysis)
    logging.debug('results: %s', results)

    return results

def to_list_of_dicts(series):
    return [{k:v} for k, v in series.iteritems()] 

class SubsequenceEngine():
    """Analyses what is the most common subsequence of a variable name"""
    def __init__(self, variables):
        self.name = 'Subsequence'
        self.variables = variables

    def analyse(self):
        cnt = Counter()
        cnt2 = Counter()

        def camel_case_split(identifier):
            matches = refinditer(
                '.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)',
                identifier)
            return [m.group(0) for m in matches]

        def under_score_split(identifier):
            return identifier.split('_')

        def get_subsequences(word):
            if is_camel(word):
                splits = camel_case_split(word)
            elif is_under(word):
                splits = under_score_split(word)
            else:
                splits = [word]
            for split in splits:
                yield split

        for var in self.variables:
            for sub in get_subsequences(var):
                if len(sub) > 1:
                    # 1 letter prefixes are too common, ignore?
                    cnt2[sub] += 1
                cnt[sub] += 1

        if len(cnt2):
            # try to get variables that are larger than 2
            most_common = cnt2.most_common(1)[0]
        else:
            most_common = cnt.most_common(1)[0]
        sub, count = most_common

        return Result(
            sub,
            'You include these characters, %s, a lot, like %s times.' %
            (sub, count))

class PrefixEngine():
    """Analyses what is the most common prefix of a variable name"""
    def __init__(self, variables):
        self.name = 'Prefix'
        self.variables = variables

    def message(self, attribute, **kwargs):
        prefix = 'You like to start your variables with {attribute} a lot. '
        suffix = 'Did it {count} times.'
        msg = prefix.format(attribute=attribute)
        msg += suffix.format(**kwargs)
        return msg

    def analyse(self):
        cnt = Counter()
        cnt2 = Counter()
        def get_prefixes(word):
            # 1 letter prefixes are too common, ignore
            return (word[:end] for end in range(1, len(word) + 1)) 
        for var in self.variables:
            for prefix in get_prefixes(var):
                if len(prefix) > 1:
                    cnt2[prefix] += 1
                cnt[prefix] += 1

        if len(cnt2):
            most_common = cnt2.most_common(1)[0]
        else:
            most_common = cnt.most_common(1)[0]

        prefix, count = most_common

        return Result(prefix, self.message(prefix, count=count))

class VerbosityEngine():
    """Analyses how concise/verbose you are based on variable name length"""
    def __init__(self, variables):
        self.name = 'Verbosity'
        self.variables = variables

    def message(self, attribute):
        prefix = suffix = ''
        if attribute == 'concise':
            prefix = 'You code concisely. '
            suffix = 'Word.'
        elif attribute == 'verbose':
            prefix = 'You code reads like prose. '
            prefix += 'I mean like Lord of the Rings. '
            suffix = 'If I had a penny for every letter you typed... '
            suffix += 'I wouldn\'t need to come to Disrupt for free food'
        else:
            suffix = 'I am confused'

        return prefix + suffix


    def analyse(self):
        import pandas as pd
        s = pd.Series(map(len, self.variables))
        mean, median = s.mean(), s.median()
        if mean < 5 or mean < median:
            style = 'concise'
        elif mean > median:
            style = 'verbose'
        else:
            style = 'confused'
        return Result(style, self.message(style))

class CasingEngine():
    """Analyses the case convention of variable names"""
    def __init__(self, variables):
        self.name = 'Casing'
        self.variables = variables

    def message(self, attribute):
        prefix = suffix = ''
        if attribute == 'camelCase':
            prefix = 'yOu coDe in caMelCasE likE tHiS.'
            suffix = 'What, are you a camel?'
        elif attribute == 'under_score':
            prefix = 'you_code_in_under_score_case_like_this'
            suffix = 'who_the_can_read_like_this____?'
        else:
            prefix = 'Your casing convention is completly neutral. '
            suffix = 'AKA boring.'

        msg = prefix + suffix
        return msg

    def analyse(self):
        cnt = Counter()
        for var in self.variables:
            cnt[case(var)] += 1

        total = sum(cnt.values())
        skew_number = total * 0.6
        case_style = 'neutral'
        # should be 20% more to skew
        if cnt['camelCase'] >= skew_number:
            case_style = 'camelCase'
        elif cnt['under_score'] >= skew_number:
            case_style = 'under_score'

        return Result(case_style, self.message(case_style))

class Result():
    """The analysis result that an engine came up with"""
    def __init__(self, attribute, reason):
        self.attribute = attribute
        self.reason = reason

    def __str__(self):
        return 'attribute: %s, reason: %s' % (self.attribute, self.reason)
    
    def to_dict(self):
        return {
            'attribute': self.attribute,
            'reason': self.reason,
        }


camel_re = re.compile(r'[a-z]+[A-Z]')

def is_camel(var):
    """e.g. isCamelCase"""
    return '_' not in var and re.match(camel_re, var) is not None
def is_under(var):
    """e.g. is_underscore_case"""
    return '_' in var
def case(var):
    if is_camel(var):
        return 'camelCase'
    elif is_under(var):
        return 'under_score'
    else:
        return 'neutral'

if __name__ == '__main__':
    unittest.main()
