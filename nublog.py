from flask import Flask, request, url_for, redirect, \
	render_template, abort, g, flash
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib
import uuid

# CONFIG #
DATABASE = 'sqlite:///./nu_twitter.db'
PER_PAGE = 30
DEBUG = True

# APP #
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['DEBUG'] = DEBUG
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)

# CONTROLLER #

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
    	g.user = db.session.query(User).get(session['user_id'])

@app.route('/')
def home():
    """Shows a feed of blog posts"""
    return render_template('home.html', posts=db.session.query(Post).order_by(Post.pub_date.desc()).limit(PER_PAGE).all())

@app.route('/posts/<post_id>')
def post(post_id):
    """Display's a post"""
    return render_template('home.html', post=db.session.query(Post).filter_by(id=post_id))

# USEFUL METHODS #
def create_post(user, body, pub_date=None):
    """Creates a post"""
    p = Post(user, body, pub_date)
    db.session.add(p)
    db.session.commit()
    return p

def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address"""
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest(), size)

def format_datetime(timestamp):
    """Format a timestamp for display"""
    return timestamp.strftime('%d/%m/%Y\n%H:%M')

# JINJA FILTERS #
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url

# MODELS #

class Post(db.Model):
    """A post table"""
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, user, body, pub_date=None):
        self.body = body

        if pub_date is None:
            pub_date = datetime.utcnow()

        self.pub_date = pub_date
        self.user = user

    def __repr__(self):
        return '<Post %r>' % self.id

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)