import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Upload Folder Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///social.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Post Model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    users = User.query.all()
    posts = Post.query.order_by(Post.created_at.desc()).all()
    
    html_content = '''
    <html>
    <head>
        <title>My Social App</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f0f2f5; }
            .box { border: 1px solid #ccc; padding: 15px; margin-bottom: 20px; border-radius: 8px; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
            .post { padding: 15px; margin-bottom: 15px; background: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            input, textarea, select { width: 100%; padding: 10px; margin: 5px 0 10px 0; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; }
            button { background-color: #1877f2; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; }
            button:hover { background-color: #166fe5; }
            video, img { width: 100%; max-height: 400px; border-radius: 8px; margin-top: 10px; background: #000; }
        </style>
    </head>
    <body>
        <h1>My Social Web App 📱🎥</h1>
        <hr>
        
        <div class="box">
            <h3>1. Create an Account (Register)</h3>
            <form action="/register" method="POST">
                <input type="text" name="username" placeholder="Enter Username" required>
                <input type="password" name="password" placeholder="Enter Password" required>
                <button type="submit">Sign Up</button>
            </form>
        </div>

        <div class="box">
            <h3>2. Create a New Post / Upload Video</h3>
            <form action="/create-post" method="POST" enctype="multipart/form-data">
                <label>Post as User:</label>
                <select name="user_id" required>
                    <option value="">-- Select User --</option>
    '''
    for user in users:
        html_content += f'<option value="{user.id}">{user.username}</option>'
        
    html_content += '''
                </select>
                <textarea name="content" rows="3" placeholder="What's on your mind? Write caption..." required></textarea>
                <label>Select Photo or Video:</label>
                <input type="file" name="file" accept="video/*,image/*">
                <button type="submit">Publish Post</button>
            </form>
        </div>
        
        <hr>
        <h2>Feeds (Recent Posts & Videos)</h2>
    '''
    
    if not posts:
        html_content += '<p>No posts yet. Be the first to share something!</p>'
    else:
        for post in posts:
            author = post.user.username if post.user else "Anonymous"
            html_content += f'''
            <div class="post">
                <strong>@{author}</strong> <small style="color:gray;">({post.created_at.strftime('%I:%M %p')})</small>
                <p style="margin-top: 8px; font-size: 16px;">{post.content}</p>
            '''
            if post.file_path:
                ext = post.file_path.rsplit('.', 1)[1].lower()
                if ext in {'mp4', 'mov'}:
                    html_content += f'<video controls src="/uploads/{post.file_path}"></video>'
                elif ext in {'png', 'jpg', 'jpeg', 'gif'}:
                    html_content += f'<img src="/uploads/{post.file_path}">'
                    
            html_content += '</div>'
            
    html_content += '''
    </body>
    </html>
    '''
    return html_content

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    existing_user = User.query.filter_by(username=username).first()
    if not existing_user:
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/create-post', methods=['POST'])
def create_post():
    user_id = request.form.get('user_id')
    content = request.form.get('content')
    file = request.files.get('file')
    
    filename = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    new_post = Post(content=content, file_path=filename, user_id=user_id)
    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)