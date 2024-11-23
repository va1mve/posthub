from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import re
from datetime import datetime

app = Flask(__name__)

API_KEY = 'pandemoniumsucks'
POSTS = 'posts.json'


def load_posts():
    if os.path.exists(POSTS):
        with open(POSTS, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"POSTS": {}}


def save_posts(posts):
    with open(POSTS, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)


@app.route('/')
def index():
    posts = load_posts()
    for post in posts['posts'].values():
        post['description'] = post['description']
    return render_template('index.html', posts=posts['posts'])


@app.route('/add', methods=['POST'])
def add_post():
    title = request.form['title']
    description = request.form['description']
    author = request.form.get('author') or 'Unknown'
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    posts = load_posts()
    
    post_id = str(len(posts['posts']))
    posts['posts'][post_id] = {
        'title': title,
        'description': description,
        'author': author,
        'date': date,
        'replies': {}
    }

    save_posts(posts)
    return redirect(url_for('index'))


@app.route('/posts/<post_id>')
def post_details(post_id):
    posts = load_posts()
    post = posts['posts'].get(post_id)
    if not post:
        return "Post not found", 404

    return render_template('post_details.html', post=post, post_id=post_id)


@app.route('/posts/<post_id>/reply', methods=['POST'])
def reply_to_post(post_id):
    content = request.form['content']
    nickname = request.form.get('nickname') or 'Unknown'
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    posts = load_posts()
    post = posts['POSTS'].get(post_id)
    if post:
        reply_id = str(len(post['replies']))
        post['replies'][reply_id] = {
            'content': content,
            'nickname': nickname,
            'date': date
        }
        save_posts(posts)

    return redirect(url_for('post_details', post_id=post_id))


# API
def authenticate(api_key):
    return api_key == API_KEY

@app.route('/api/create_post', methods=['POST'])
def api_create_post():
    api_key = request.args.get('api_key')
    
    if not authenticate(api_key):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    title = data.get('title')
    description = data.get('description')
    author = data.get('author') or 'Unknown'
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    posts = load_posts()
    post_id = str(len(posts['posts']))
    posts['posts'][post_id] = {
        'title': title,
        'description': description,
        'author': author,
        'date': date,
        'replies': {}
    }
    
    save_posts(posts)
    return jsonify({"success": True, "post_id": post_id}), 201

@app.route('/api/delete_post/<post_id>', methods=['DELETE'])
def api_delete_post(post_id):
    api_key = request.args.get('api_key')
    
    if not authenticate(api_key):
        return jsonify({"error": "Unauthorized"}), 401
    
    posts = load_posts()
    
    if post_id in posts['posts']:
        del posts['posts'][post_id]
        save_posts(posts)
        return jsonify({"success": True}), 200
    
    return jsonify({"error": "Post not found"}), 404

@app.route('/api/delete_comment/<post_id>/<reply_id>', methods=['DELETE'])
def api_delete_comment(post_id, reply_id):
    api_key = request.args.get('api_key')
    
    if not authenticate(api_key):
        return jsonify({"error": "Unauthorized"}), 401

    posts = load_posts()
    post = posts['posts'].get(post_id)
    
    if post and reply_id in post['replies']:
        del post['replies'][reply_id]
        save_posts(posts)
        return jsonify({"success": True}), 200
    
    return jsonify({"error": "Comment not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)