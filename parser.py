import subprocess

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

if __name__ == '__main__':
    unittest.main()
