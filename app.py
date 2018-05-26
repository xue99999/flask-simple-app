#!/usr/bin/env python3

import os
import json
from flask import Flask, render_template, abort

app = Flask(__name__)
app.config['TEMPLATES_NOT_RELOAD'] = True

base = '/home/shiyanlou/files'

def _get_list():
    json_files = []
    for x in os.listdir(base):
        name, type = x.split('.')
        if type == 'json':
            json_files.append(os.path.join(base, x))
        else:
            print('file is not json type')
    return json_files

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route('/')
def index():
    
    json_files = _get_list()
    if len(json_files) <= 0:
        abort(404)
    text_list = []
    for file in json_files:
        with open(file) as f:
            dct = json.loads(f.read())
            text_list.append(dct) 

    return render_template('index.html', names=text_list)

@app.route('/files/<filename>')
def file(filename):
    filename = filename + '.json'
    file = os.path.join(base, filename)

    if os.path.exists(file):
        with open(file) as f:
            dct = json.loads(f.read())
    else:
        abort(404)

    return render_template('file.html', article=dct)

