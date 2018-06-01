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
    
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    created_time = db.Column(db.DateTime)
    content = db.Column(db.Text)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
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
        file_item = mongo_db.files.find_one({'file_id': self.id})
        if file_item:
            tags = file_item['tags']
            if tag_name not in tags:
                tags.append(tag_name)
            mongo_db.files.update_one({'file_id': self.id}, {'$set': {'tags': tags}})
        else:
            tags = [tag_name]
            mongo_db.files.insert_one({'file_id': self.id, 'tags': tags})

        return tags

        
    def remove_tag(self, tag_name):
        file_item = mongo_db.files.find_one({'file_id': self.id})
        if file_item:
            tags = file_item['tags']
            if tag_name in tags:
                tags.remove(tag_name)
                new_tags = tags
                mongo_db.files.update_one({'file_id': self.id},{'$set': {'tags': new_tags}})
                return new_tags
            return []

    @property
    def tags(self):
        file_item = mongo_db.files.find_one({'file_id': self.id})
        if file_item:
            print(file_item)
            return file_item['tags']
        else:
            return []

class Category(db.Model):

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.name


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route('/')
def index():
    
    return render_template('index.html', names=File.query.all())

@app.route('/files/<file_id>')
def file(file_id):
    file = File.query.filter_by(id=file_id).first()
    if file: 
        article = file
    else:
        abort(404)

    return render_template('file.html', article=article)


if __name__ == '__main__':


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
    
