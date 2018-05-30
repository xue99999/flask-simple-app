#!/usr/bin/env python3

import os
import json
from datetime import datetime
from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient

app = Flask(__name__)
app.config['TEMPLATES_NOT_RELOAD'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/shiyanlou'

db = SQLAlchemy(app)

client = MongoClient('127.0.0.1', 27017)
mongo_db = client.shiyanlou

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

    def add_tag(self, tag_name):
        file = mongo_db.file.find({'id': self.id})
        if file:
            tags = file.tags
            if tag_name not in tags:
                tags.append(tag_name)
                mongo_db.file.update_one({'id': self.id, 'tags': tags})
        else:
            mongo_db.file.insert_one({'id': self.id, 'tags': [tag_name]})

        
    def remove_tag(self, tag_name):
        file = mongo_db.file.find({'id': self.id})
        if file:
            tags = file.tags 
            if tag_name in tags:
                idx = tags.index(tag_name)
                tags.pop(idx)
                mongo_db.file.update_one({'id': self.id, 'tags': tags})




    @property
    def tags(self):
        tag_list = mongo_db.file.find({'id': self.id})
        return tag_list

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.name

base = '/home/shiyanlou/files'


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route('/')
def index():
    file = File.query.all()
    
    return render_template('index.html', names=file)

@app.route('/files/<file_id>')
def file(file_id):
    file = File.query.filter_by(id=file_id).first()
    if file: 
        article = file
    else:
        abort(404)

    return render_template('file.html', article=article)

#create table and data
db.create_all()
java = Category('Java')
python = Category('Python')
file1 = File('Hello Java', 'File Content - Java is cool!', java)
file2 = File('Hello Python', 'File Content - Python is cool!', python)
db.session.add(java)
db.session.add(python)
db.session.add(file1)
db.session.add(file2)
db.session.commit()

file1.add_tag('tech')
file1.add_tag('java')
file1.add_tag('linux')
file2.add_tag('tech')
file2.add_tag('python')
