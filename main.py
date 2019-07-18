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
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')  

    def __init__(self, username, password):
        self.username = username
        self.password = password  

@app.before_request
def require_login():
    accepted_routes = ['index', 'signup', 'login', 'blog']
    if not ('user' in session or request.endpoint in accepted_routes):
        return redirect("/signup")

@app.route('/')
def index():
    all_usernames = User.query.all()
    one_user = request.args.get('id')
    if one_user != None:
        user = User.query.get(one_user)
        blog = Blog.query.filter_by(owner_id=one_user)
        return render_template("one_user.html", user=user, blog=blog)
    return render_template('index.html', title='Home', all_usernames=all_usernames)

@app.route('/blog')
def blog():
    posts = Blog.query.all()
    return render_template('blog.html', title='Build A Blog', posts=posts)

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user or password != user.password:
            flash("That email password combination does not exist")
            return redirect('/login')

        session['user'] = username
        return redirect('/add')

    return render_template('login.html')  

@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect("/blog")      

@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        if len(username) < 3:
            flash("Username needs to be a least 3 characters long")
            return redirect('/signup')
        password = request.form['password']
        verify = request.form['verify'] 
        if password != verify:
            flash("Passwords do not match")
            return redirect('/signup')
        if len(password) < 3:
            flash("Password need to be at least 3 characters long")
            return redirect('/signup')    

        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            flash("This username already exists")
            return redirect('/signup')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.username
        return render_template('add.html')
    else:  
        return render_template('/signup.html')
   

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Blog.query.filter_by(id=post_id).one()
    return render_template('/post.html', post=post)    

@app.route('/add')
def add():
    return render_template('add.html')      

@app.route('/newpost', methods=['POST'])
def newpost():

    owner = User.query.filter_by(username=session['user']).first()    

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        body = request.form['body']  
        post = Blog(blog_title, body, owner) 
        db.session.add(post)
        db.session.commit() 

    return render_template('post.html', post=post)   
  

if __name__ == '__main__':
    app.run()
           