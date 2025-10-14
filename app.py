from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Response, stream_with_context
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import praw
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reddit_sorter.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    color = db.Column(db.String(7), default='#007bff')  # Hex color code
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('RedditPost', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class RedditPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reddit_id = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50))
    subreddit = db.Column(db.String(50))
    url = db.Column(db.Text)
    selftext = db.Column(db.Text)
    score = db.Column(db.Integer)
    num_comments = db.Column(db.Integer)
    created_utc = db.Column(db.DateTime)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    permalink = db.Column(db.Text)
    is_self = db.Column(db.Boolean, default=False)
    thumbnail = db.Column(db.String(200))
    preview_url = db.Column(db.String(500))

    def __repr__(self):
        return f'<RedditPost {self.reddit_id}: {self.title[:50]}...>'

# Initialize Reddit API
def get_reddit_instance():
    return praw.Reddit(
        client_id=os.environ.get('REDDIT_CLIENT_ID'),
        client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
        user_agent=os.environ.get('REDDIT_USER_AGENT', 'RedditSorter/1.0 by YourUsername'),
        username=os.environ.get('REDDIT_USERNAME'),
        password=os.environ.get('REDDIT_PASSWORD')
    )

@app.route('/')
def index():
    categories = Category.query.all()
    posts = RedditPost.query.order_by(RedditPost.saved_at.desc()).limit(20).all()
    return render_template('index.html', categories=categories, posts=posts)

@app.route('/fetch_saved_posts')
def fetch_saved_posts():
    # Redirect to the live progress page
    return render_template('fetch_progress.html')

@app.route('/fetch_saved_posts_stream')
def fetch_saved_posts_stream():
    def generate():
        try:
            yield f"data: {json.dumps({'type': 'info', 'message': 'Connecting to Reddit API...'})}\n\n"
            time.sleep(0.5)
            
            reddit = get_reddit_instance()
            user = reddit.user.me()
            
            yield f"data: {json.dumps({'type': 'success', 'message': f'Connected as u/{user.name}'})}\n\n"
            time.sleep(0.5)
            
            yield f"data: {json.dumps({'type': 'info', 'message': 'Fetching saved posts...'})}\n\n"
            time.sleep(0.5)
            
            new_posts = 0
            skipped_posts = 0
            total_processed = 0
            
            for submission in user.saved(limit=100):  # Fetch last 100 saved posts
                total_processed += 1
                
                # Check if post already exists
                existing_post = RedditPost.query.filter_by(reddit_id=submission.id).first()
                if not existing_post:
                    # Create new post record
                    try:
                        post = RedditPost(
                            reddit_id=submission.id,
                            title=submission.title,
                            author=str(submission.author) if submission.author else '[deleted]',
                            subreddit=submission.subreddit.display_name,
                            url=submission.url,
                            selftext=submission.selftext if submission.selftext else '',
                            score=submission.score,
                            num_comments=submission.num_comments,
                            created_utc=datetime.fromtimestamp(submission.created_utc),
                            permalink=f"https://reddit.com{submission.permalink}",
                            is_self=submission.is_self,
                            thumbnail=submission.thumbnail if submission.thumbnail != 'self' else None,
                            preview_url=submission.preview['images'][0]['source']['url'] if hasattr(submission, 'preview') and submission.preview and submission.preview.get('images') else None
                        )
                        db.session.add(post)
                        db.session.commit()
                        new_posts += 1
                        
                        yield f"data: {json.dumps({'type': 'post_added', 'message': f'Added: {submission.title[:60]}...', 'subreddit': submission.subreddit.display_name, 'new': new_posts, 'skipped': skipped_posts, 'total': total_processed})}\n\n"
                    except Exception as e:
                        db.session.rollback()
                        yield f"data: {json.dumps({'type': 'warning', 'message': f'Error saving post: {str(e)[:50]}'})}\n\n"
                else:
                    skipped_posts += 1
                    if skipped_posts % 10 == 0:  # Show progress every 10 skipped posts
                        yield f"data: {json.dumps({'type': 'post_skipped', 'message': f'Skipping already saved posts...', 'new': new_posts, 'skipped': skipped_posts, 'total': total_processed})}\n\n"
                
                time.sleep(0.1)  # Small delay to make progress visible
            
            yield f"data: {json.dumps({'type': 'info', 'message': f'Processing complete! Processed {total_processed} posts.'})}\n\n"
            yield f"data: {json.dumps({'type': 'success', 'message': f'Successfully added {new_posts} new posts! ({skipped_posts} already existed)'})}\n\n"
            yield f"data: {json.dumps({'type': 'complete', 'new': new_posts, 'skipped': skipped_posts, 'total': total_processed})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Error: {str(e)}'})}\n\n"
            db.session.rollback()
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/categories')
def categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/create_category', methods=['POST'])
def create_category():
    name = request.form.get('name').strip()
    color = request.form.get('color', '#007bff')
    
    if not name:
        flash('Category name is required!', 'error')
        return redirect(url_for('categories'))
    
    existing = Category.query.filter_by(name=name).first()
    if existing:
        flash('Category with this name already exists!', 'error')
        return redirect(url_for('categories'))
    
    category = Category(name=name, color=color)
    db.session.add(category)
    db.session.commit()
    
    flash(f'Category "{name}" created successfully!', 'success')
    return redirect(url_for('categories'))

@app.route('/update_category/<int:category_id>', methods=['POST'])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    category.name = request.form.get('name').strip()
    category.color = request.form.get('color', '#007bff')
    
    if not category.name:
        flash('Category name is required!', 'error')
        return redirect(url_for('categories'))
    
    db.session.commit()
    flash(f'Category "{category.name}" updated successfully!', 'success')
    return redirect(url_for('categories'))

@app.route('/delete_category/<int:category_id>')
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    # Move posts in this category to uncategorized
    posts_in_category = RedditPost.query.filter_by(category_id=category_id).all()
    for post in posts_in_category:
        post.category_id = None
    
    db.session.delete(category)
    db.session.commit()
    
    flash(f'Category "{category.name}" deleted successfully!', 'success')
    return redirect(url_for('categories'))

@app.route('/assign_category/<int:post_id>', methods=['POST'])
def assign_category(post_id):
    post = RedditPost.query.get_or_404(post_id)
    category_id = request.form.get('category_id')
    
    if category_id:
        category_id = int(category_id)
        category = Category.query.get(category_id)
        if category:
            post.category_id = category_id
        else:
            flash('Invalid category selected!', 'error')
            return redirect(url_for('index'))
    else:
        post.category_id = None
    
    db.session.commit()
    flash('Post category updated successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/posts')
def posts():
    category_id = request.args.get('category_id', type=int)
    show_uncategorized = request.args.get('uncategorized', type=str)
    search = request.args.get('search', '').strip()
    
    query = RedditPost.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    elif show_uncategorized == 'true':
        # Show only posts without a category
        query = query.filter_by(category_id=None)
    
    if search:
        query = query.filter(RedditPost.title.contains(search))
    
    posts = query.order_by(RedditPost.saved_at.desc()).all()
    categories = Category.query.all()
    
    return render_template('posts.html', posts=posts, categories=categories, 
                         selected_category_id=category_id, search_term=search, 
                         show_uncategorized=show_uncategorized)

@app.route('/api/posts')
def api_posts():
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '').strip()
    
    query = RedditPost.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(RedditPost.title.contains(search))
    
    posts = query.order_by(RedditPost.saved_at.desc()).all()
    
    return jsonify([{
        'id': post.id,
        'title': post.title,
        'author': post.author,
        'subreddit': post.subreddit,
        'url': post.url,
        'score': post.score,
        'num_comments': post.num_comments,
        'created_utc': post.created_utc.isoformat() if post.created_utc else None,
        'saved_at': post.saved_at.isoformat(),
        'category_id': post.category_id,
        'category_name': post.category.name if post.category else None,
        'category_color': post.category.color if post.category else None,
        'permalink': post.permalink,
        'is_self': post.is_self,
        'thumbnail': post.thumbnail,
        'preview_url': post.preview_url
    } for post in posts])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default "Uncategorized" category if it doesn't exist
        if not Category.query.filter_by(name='Uncategorized').first():
            uncategorized = Category(name='Uncategorized', color='#6c757d')
            db.session.add(uncategorized)
            db.session.commit()
    
    app.run(debug=True)
