from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import datetime
import uuid
import os

app = Flask(__name__)
con = sqlite3.connect("dz12db")
cur = con.cursor()

def has_access(uuid):
    if 'posts' in session:
        if uuid in session['posts']:
            return True
        return False
    return False

@app.route("/", methods=['POST', 'GET'])
def main():
    if request.method == 'POST':
        cur.execute("""DELETE FROM Posts WHERE uuid=?""", [request.form['uuid']]
               )
        con.commit()

    cur.execute("SELECT id, title, description, date, uuid FROM Posts")

    posts = [{'id': post[0], 'title': post[1], 'description': post[2], 'date': post[3], 'uuid': post[4], 'hasAccess': has_access(post[4])} for post in cur.fetchall()]

    if(len(posts) > 1):
        for post in posts:
            if (datetime.datetime.now() - datetime.datetime.strptime(post['date'], "%Y-%m-%d %H:%M:%S.%f")).total_seconds() > 300:
                cur.execute("""DELETE FROM Posts WHERE uuid=?""", [post['uuid']])
                con.commit()

    return render_template('./index.html', posts=posts)

@app.route("/post", methods=['GET'])
def post():
    post_uuid = request.args.get('uuid')
    cur.execute("SELECT id, title, description, date, uuid FROM Posts WHERE uuid=?", [post_uuid])

    posts = [{'id': post[0], 'title': post[1], 'description': post[2], 'date': post[3], 'uuid': post[4]} for post in cur.fetchall()]

    return render_template('./post.html', posts=posts)

@app.route("/add", methods=['POST', 'GET'])
def add():
    if request.method == 'POST':

        if request.form['title'] and request.form['description']:
            post_uuid = uuid.uuid4()
            cur.execute("""INSERT INTO Posts (title, description, date, uuid)
                  VALUES (?, ?, ?, ?)""", [request.form['title'], request.form['description'],  datetime.datetime.now(), str(post_uuid)]
               )
            con.commit()
            if 'posts' in session:
                session['posts'] += [str(post_uuid)]
            else:
                session['posts'] = [str(post_uuid)]
            return redirect(url_for('main'))
        else:
            return redirect(url_for('error'))
    return render_template('./add.html')

@app.route("/edit", methods=['POST', 'GET'])
def edit():
    if request.method == 'POST':
        if request.form['title'] and request.form['description']:
            post_uuid = request.form['uuid']
            cur.execute("""UPDATE Posts SET title=?, description=?, date=?, uuid=?
                 WHERE uuid=?""", [request.form['title'], request.form['description'],  datetime.datetime.now(), str(post_uuid), post_uuid]
               )
            con.commit()
            return redirect(url_for('main'))
        else:
            return redirect(url_for('error'))

    post_uuid = request.args.get('uuid')
    cur.execute("SELECT id, title, description, date, uuid FROM Posts WHERE uuid=?", [post_uuid])
    post = [{'id': post[0], 'title': post[1], 'description': post[2], 'date': post[3], 'uuid': post[4]} for post in cur.fetchall()][0]
    
    return render_template('./edit.html', post=post)

@app.route("/error")
def error():
    return render_template('./error.html')

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(threaded=False)