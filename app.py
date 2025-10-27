from flask import Flask, render_template, flash, redirect, url_for, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# init app
app = Flask(__name__)
app.config.from_object(Config)

# init extenstions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# import models and forms after initializing db
from models import User, Post, Comment, Vote
from forms import LoginForm, RegistrationForm, PostForm, CommentForm

@app.route('/')
@app.route('/index')
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user, channel=form.channel.data)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))

    selected_channel = request.args.get('channel', 'general')
    posts = Post.query.filter_by(channel=selected_channel).order_by(Post.timestamp.desc()).all()

    # get available channels from dropdown
    channels = [choice[0] for choice in form.channel.choices]

    return render_template('index.html', title='Synapse', form=form, posts=posts, selected_channel=selected_channel, channels=channels)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not check_password_hash(user.password_hash, form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        # else
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html', title='Log In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User()
        user.password_hash = generate_password_hash(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered Synapser!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(body=form.body.data, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!')
        return redirect(url_for('view_post', post_id=post.id))

    comments = post.comments.order_by(Comment.timestamp.asc()).all()
    user_vote = Vote.query.filter_by('view_post', post_id=post_id).first()

    return render_template('post.html', title=f'Synapse by {post.author.username}', post=post, comments=comments, form=form, user_vote=user_vote)

@app.route('/upvote/<int:post_id>')
@login_required
def upvote(post_id):
    post = Post.query.get_or_404(post_id)
    vote = Vote.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if vote:
        if vote.value == 1: # already upvoted, delete the vote
            db.session.delete(vote)
            flash('Upvote removed!')
        else: # downvoted, change to upvote, like reddit
            vote.value = 1
            flash('Changed to upvote!')

    else: # no vote yet, upvote
        new_vote = Vote(user_id=current_user.id, post_id=post_id, value=1)
        db.session.add(new_vote)
        flash('Upvoted!')

    db.session.commit()
    return redirect(request.referrer or url_for('index')) # redirect back to the page where the user was from

@app.route('/downvote/<int:post_id>')
@login_required
def downvote(post_id):
    post = Post.query.get_or_404(post_id)
    vote = Vote.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if vote:
        if vote.value == -1: # already downvote, delete the vote
            db.session.delete(vote)
            flash('Downvote removed!')
        else: # upvoted, change to downvote
            vote.value = -1
            flash('Changed to downvote!')

    else:  # no vote yet, downvote
        new_vote = Vote(user_id=current_user.id, post_id=post_id, value=-1)
        db.session.add(new_vote)
        flash('Downvoted!')

    db.session.commit()
    return redirect(request.referrer or url_for('index'))

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


# error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# running app:
if __name__ == '__main__':
    app.run(debug=True)


