from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vocab.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/audio'
app.secret_key = 'your-very-secret-key' 

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    english = db.Column(db.Text)
    french = db.Column(db.Text)
    pronunciation = db.Column(db.Text)  # handles full sentences or IPA transcription
    audio_file = db.Column(db.String(200))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Routes
@app.route('/')
def index():
    topics = Topic.query.order_by(Topic.created_at.desc()).all()
    return render_template('index.html', topics=topics)

@app.route('/add_topic', methods=['POST'])
def add_topic():
    name = request.form.get('name')
    description = request.form.get('description')
    
    if name:
        db.session.add(Topic(name=name, description=description))
        db.session.commit()
    flash("Topic Added successfully.", "success")
    return redirect(url_for('index'))

@app.route('/topic/<int:topic_id>')
def view_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    words = Word.query.filter_by(topic_id=topic_id).order_by(Word.created_at).all()
    return render_template('topic.html', topic=topic, words=words)

@app.route('/add_word/<int:topic_id>', methods=['POST'])
def add_word(topic_id):
    english = request.form.get('english')
    french = request.form.get('french')
    pronunciation = request.form.get('pronunciation')
    audio = request.files.get('audio_file')
    filename = ''
    if audio:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], audio.filename)
        audio.save(filename)
    new_word = Word(english=english, french=french, pronunciation=pronunciation, audio_file=filename, topic_id=topic_id)
    db.session.add(new_word)
    db.session.commit()
    flash("Word added successfully.", "success")
    return redirect(url_for('view_topic', topic_id=topic_id))

@app.route('/update_word/<int:word_id>', methods=['POST'])
def update_word(word_id):
    word = Word.query.get_or_404(word_id)
    word.english = request.form.get('english')
    word.french = request.form.get('french')
    word.pronunciation = request.form.get('pronunciation')
    audio = request.files.get('audio_file')
    if audio:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], audio.filename)
        audio.save(filename)
        word.audio_file = filename
    db.session.commit()
    flash("Word updated successfully.", "success")
    return redirect(url_for('view_topic', topic_id=word.topic_id))

@app.route('/delete_word/<int:word_id>', methods=['GET'])
def delete_word(word_id):
    word = Word.query.get_or_404(word_id)
    
    # Optional: delete the associated audio file from disk
    if word.audio_file:
        audio_path = os.path.join(app.root_path, word.audio_file)
        if os.path.exists(audio_path):
            os.remove(audio_path)

    db.session.delete(word)
    db.session.commit()
    flash("Word deleted successfully.", "success")
    return redirect(url_for('view_topic', topic_id=word.topic_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')
