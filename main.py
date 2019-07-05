from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    body = db.Column(db.Text)

@app.route('/')
def index():
    posts = Blog.query.all()

    return render_template('blog.html', title='Build A Blog', posts=posts)

@app.route('/add')
def add():
    return render_template('add.html')    

@app.route('/newpost', methods=['POST'])
def newpost():
    blog_title = request.form['blog_title']
    body = request.form['body']  

    post = Blog(blog_title=blog_title, body=body) 

    db.session.add(post)
    db.session.commit()  

    blog_title_error = ''
    body_error = ''

    if blog_title == '':
        blog_title_error = "Please fill out title."
    if body == '':
        body_error = "Please fill out body content." 
    if blog_title_error != '' or body_error != '':
        return render_template('/add.html', blog_title=blog_title, 
        body=body, blog_title_error=blog_title_error, 
        body_error=body_error)           
    else:
        return redirect('/')

if __name__ == '__main__':
    app.run()
           