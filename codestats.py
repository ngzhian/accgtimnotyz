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
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')

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
    # prefer URL to snippet
    snippet = request.form['snippet']
    url = request.form['url']
    fid = request.form['fid']

    if not snippet and not url:
        return jsonify()

    if url:
        resp = requests.get(url)
        snippet = resp.content.decode('utf-8')
        results = snippet_to_results(snippet)
    elif snippet:
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
           '{sid}/Messages'.format(sid=TWILIO_SID))
    from_number = '+12015966238'
    to_number = NUMBER[fid]
    view_url = url_for('show_stats', fid=fid)
    requests.post(
        url, {
            'From': from_number,
            'To': to_number,
            'Body': 'It\'s ready! Go to %s' % view_url
        },
        auth=(TWILIO_SID, TWILIO_TOKEN))


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
