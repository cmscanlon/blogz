from flask import Flask, request, redirect, render_template, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'AW241dh3On'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blog_title, body, owner):
        self.blog_title = blog_title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')  

    def __init__(self, email, password):
        self.email = email
        self.password = password  

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/')
def index():
    posts = Blog.query.all()

    return render_template('blog.html', title='Build A Blog', posts=posts)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return render_template('add.html')
    else:
        flash('User password incorrect, or user does not exist', 'error')
        return render_template('login.html')    

# User enters a username that is stored in the database with the correct password and is 
#     redirected to the /newpost page with their username being stored in a session.

# User enters a username that is stored in the database with an incorrect password and is 
#     redirected to the /login page with a message that their password is incorrect.

# User tries to login with a username that is not stored in the database and is 
#     redirected to the /login page with a message that this username does not exist.

# User does not have an account and clicks "Create Account" and is directed to the /signup page.

@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify'] 

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            flash("That username already exists, either login if this is you or pick another username.")   

    return render_template('add.html')

@app.route('/logout', methods = ['POST'])
def logout():
    del session['email']
    return redirect('/')    

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Blog.query.filter_by(id=post_id).one()

    return render_template('/post.html', post=post)    

@app.route('/add')
def add():
    return render_template('add.html')    

@app.route('/newpost', methods=['POST'])
def newpost():

    owner = User.query.filter_by(email=session['email']).first()
    
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        body = request.form['body']  
        new_blog = Blog(blog_title, body, owner)

        post = Blog(blog_title=blog_title, body=body, owner=owner)  

        db.session.add(post)
        db.session.commit() 
        session['email'] = email

    

    return render_template('/post.html', post=post)

if __name__ == '__main__':
    app.run()
           