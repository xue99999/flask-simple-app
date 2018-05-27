#!/usr/bin/env python3

import os
import json
from datetime import datetime
from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
app.config['TEMPLATES_NOT_RELOAD'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/shiyanlou'

db = SQLAlchemy(app)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    created_time = db.Column(db.DateTime)
    content = db.Column(db.Text)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, title, content, category, created_time=None):
        self.title = title
        self.content = content
        self.category = category

        if created_time is None:
            created_time = datetime.utcnow()
        self.created_time = created_time
            

    def __repr__(self):
        return '<File %r>' % self.title

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.name

base = '/home/shiyanlou/files'

'''
def _get_list():
    json_files = []
    for x in os.listdir(base):
        name, type = x.split('.')
        if type == 'json':
            json_files.append(os.path.join(base, x))
        else:
            print('file is not json type')
    return json_files
'''

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route('/')
def index():
    Session = sessionmaker(bind=engine)
    session = Session()
    file = session.query(File).first()
    
    return render_template('index.html', names=file)

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

