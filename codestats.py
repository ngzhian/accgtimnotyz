from functools import lru_cache
import os
import tempfile

from flask import Flask, render_template, request

from analyse import analyse
from parser import get_var_names

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')

# takes a github repo url to analyse
@app.route('/g', methods=['GET', 'POST'])
def github_repo():
    return "Not implemented"

# takes a JS snippet to analyse
@app.route('/s', methods=['GET', 'POST'])
def js_snippet():
    if request.method == 'POST':
        snippet = request.form['snippet']
        results = snippet_to_results(snippet)
        return render_template('snippet.html', results=results)

    return "analyse"

@lru_cache(maxsize=32)
def snippet_to_results(snippet):
    fd, path = tempfile.mkstemp('.js')
    results = None

    # need to do this to flush the file
    with open(path, 'w') as f:
        f.write(snippet)

    with open(path, 'r') as f:
        variables = get_var_names(fullpath=path)
        # finally get interest statistics
        results = analyse(variables)
    return results


# how to get github integartion?
# how to pick which files to look at
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
