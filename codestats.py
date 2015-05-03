from functools import lru_cache
import os
import tempfile

from flask import Flask, render_template, request, redirect, jsonify, url_for
import requests

from analyse import analyse
from parser import get_var_names

import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

# takes a github repo url to analyse
@app.route('/g', methods=['GET', 'POST'])
def github_repo():
    return "Not implemented"

STORE = {}

# takes a JS snippet to analyse
@app.route('/s/<fid>', methods=['GET'])
def show_stats(fid):
    if fid in STORE:
        # if get ,resder template with 
        return render_template('snippet.html', results=STORE[fid])
    else:
        return redirect(url_for('index'))


# renders the analysis of a snippet of js
@app.route('/s', methods=['POST'])
def js_snippet():
    # if post, return random number with
    snippet = request.form['snippet']
    fid = request.form['fid']
    results = snippet_to_results(snippet)

    logging.debug('FID: %s', fid)
    STORE[fid] = results
    maybe_send_text(fid)


    url = url_for('show_stats', fid=fid)
    return jsonify(fid=fid, url=url)

NUMBER = {}

@app.route('/t', methods=['POST'])
def save_number_to_sms():
    number = request.form['number']
    fid = request.form['fid']

    logging.debug('SAVE NUMBER: %s', number)

    NUMBER[fid] = number
    return jsonify(
        message='Saved, we\'ll text %s when it\'s done.' % number)

def maybe_send_text(fid):
    if fid in STORE and fid in NUMBER:
        send_sms(fid)

def send_sms(fid):
    if fid not in NUMBER:
        return

    url = ('https://api.twilio.com/2010-04-01/Accounts/'
           'AC8d2bfcff457395a5ea4f23a2eaf005b9/Messages')
    from_number = '+12015966238'
    to_number = NUMBER[fid]
    view_url = url_for('show_stats', fid=fid)
    requests.post(
        url, {
            'From': from_number,
            'To': to_number,
            'Body': 'It\'s ready! Go to %s' % view_url
        },
        auth=('AC8d2bfcff457395a5ea4f23a2eaf005b9',
            '48136ece4272965c9018d241e5b47d15'))


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
