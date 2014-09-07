from flask import Flask, request, url_for, redirect, \
	render_template, abort
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib
import uuid

# CONFIG #
DATABASE = 'sqlite:///./nu_blog.db'
PER_PAGE = 30
DEBUG = True

# APP #
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.debug = DEBUG
db = SQLAlchemy(app)

# CONTROLLER #
@app.route('/')
def home():
    """Shows a feed of blog posts"""
    return render_template('home.html', posts=db.session.query(Post).order_by(Post.pub_date.desc()).limit(PER_PAGE).all())

@app.route('/about')
def about():
    """Shows an about page"""
    return render_template('about.html')

@app.route('/posts/<post_id>')
def post(post_id):
    """Display's a post"""
    return render_template('post.html', post=db.session.query(Post).get(post_id))

# USEFUL METHODS #
def create_post(title, body, pub_date=None):
    """Creates a post"""
    p = Post(title, body, pub_date)
    db.session.add(p)
    db.session.commit()
    return p

def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address"""
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest(), size)

def format_datetime(timestamp):
    """Format a timestamp for display"""
    return timestamp.strftime('%d %B, %Y')

def first_eighty_characters(body):
    """Returns the first 80 characters of given body"""
    return body[:81]

# JINJA FILTERS #
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url
app.jinja_env.filters['eighty_chars'] = first_eighty_characters

# MODELS #
class Post(db.Model):
    """A post table"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)

    def __init__(self, title, body, pub_date=None):
        self.title = title
        self.body = body

        if pub_date is None:
            pub_date = datetime.utcnow()

        self.pub_date = pub_date

    def __repr__(self):
        return '<Post %r>' % self.id

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)