from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration - နာမည်အသစ်ပေးထားပါတယ်
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///final_social_v4.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Initialize Database
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    # ဒီမှာ home.html ကို ခေါ်ထားပါတယ်
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
