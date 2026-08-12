import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, g

app = Flask(__name__)

# Use environment variable for secret key with a fallback
app.secret_key = os.environ.get('SECRET_KEY', 'quicknotes-secret-key-change-in-production')

# Absolute path to ensure SQLite database works reliably regardless of working directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'quicknotes.db')


def get_db():
    """Returns an active SQLite database connection stored on Flask's request context."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        # Enable foreign key constraints in SQLite
        db.execute("PRAGMA foreign_keys = ON;")
    return db


@app.teardown_appcontext
def close_connection(exception):
    """Closes the database connection at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    """Creates database tables automatically if they do not exist."""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Create subjects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                is_favorite INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
            )
        ''')
        db.commit()


# Initialize database schemas
init_db()


# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------

@app.route('/')
def index():
    """Home page: Displays subjects summary, recent notes, and search entry."""
    db = get_db()
    
    # Fetch all subjects with note counts
    subjects = db.execute('''
        SELECT s.id, s.name, COUNT(n.id) AS note_count
        FROM subjects s
        LEFT JOIN notes n ON s.id = n.subject_id
        GROUP BY s.id
        ORDER BY s.name ASC
    ''').fetchall()
    
    # Fetch 6 most recently updated notes
    recent_notes = db.execute('''
        SELECT n.id, n.title, n.content, n.is_favorite, n.updated_at, s.name AS subject_name
        FROM notes n
        JOIN subjects s ON n.subject_id = s.id
        ORDER BY n.updated_at DESC
        LIMIT 6
    ''').fetchall()
    
    return render_template('index.html', subjects=subjects, recent_notes=recent_notes)


@app.route('/subjects', methods=['GET', 'POST'])
def subjects():
    """Subjects page: Lists all subjects with note counts and subject creation modal/form."""
    db = get_db()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            try:
                db.execute('INSERT INTO subjects (name) VALUES (?)', (name,))
                db.commit()
                flash('Subject created successfully!', 'success')
            except sqlite3.IntegrityError:
                flash('A subject with that name already exists.', 'error')
        return redirect(url_for('subjects'))

    all_subjects = db.execute('''
        SELECT s.id, s.name, s.created_at, COUNT(n.id) AS note_count
        FROM subjects s
        LEFT JOIN notes n ON s.id = n.subject_id
        GROUP BY s.id
        ORDER BY s.name ASC
    ''').fetchall()
    
    return render_template('subjects.html', subjects=all_subjects)


@app.route('/subject/<int:subject_id>')
def subject_detail(subject_id):
    """Displays all notes belonging to a specific subject."""
    db = get_db()
    
    subject = db.execute('SELECT * FROM subjects WHERE id = ?', (subject_id,)).fetchone()
    if not subject:
        flash('Subject not found.', 'error')
        return redirect(url_for('subjects'))
        
    notes = db.execute('''
        SELECT * FROM notes 
        WHERE subject_id = ? 
        ORDER BY is_favorite DESC, updated_at DESC
    ''', (subject_id,)).fetchall()
    
    return render_template('notes.html', subject=subject, notes=notes)


@app.route('/subject/add', methods=['GET', 'POST'])
def add_subject():
    """Adds a new subject."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            db = get_db()
            try:
                db.execute('INSERT INTO subjects (name) VALUES (?)', (name,))
                db.commit()
                flash('Subject added successfully!', 'success')
            except sqlite3.IntegrityError:
                flash('A subject with that name already exists.', 'error')
        return redirect(url_for('subjects'))
    return redirect(url_for('subjects'))


@app.route('/subject/delete/<int:subject_id>', methods=['POST', 'GET'])
def delete_subject(subject_id):
    """Deletes a subject and all associated notes."""
    db = get_db()
    db.execute('DELETE FROM subjects WHERE id = ?', (subject_id,))
    db.commit()
    flash('Subject deleted.', 'info')
    return redirect(url_for('subjects'))


@app.route('/note/add/<int:subject_id>', methods=['GET', 'POST'])
def add_note(subject_id):
    """Creates a new note inside a specific subject."""
    db = get_db()
    subject = db.execute('SELECT * FROM subjects WHERE id = ?', (subject_id,)).fetchone()
    
    if not subject:
        flash('Subject does not exist.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip() or 'Untitled Note'
        content = request.form.get('content', '')
        is_favorite = 1 if request.form.get('is_favorite') else 0
        
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO notes (subject_id, title, content, is_favorite)
            VALUES (?, ?, ?, ?)
        ''', (subject_id, title, content, is_favorite))
        db.commit()
        
        flash('Note created!', 'success')
        return redirect(url_for('subject_detail', subject_id=subject_id))

    return render_template('editor.html', note=None, subject=subject)


@app.route('/note/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    """Views or edits an existing note."""
    db = get_db()
    note = db.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    
    if not note:
        flash('Note not found.', 'error')
        return redirect(url_for('index'))

    subject = db.execute('SELECT * FROM subjects WHERE id = ?', (note['subject_id'],)).fetchone()

    if request.method == 'POST':
        title = request.form.get('title', '').strip() or 'Untitled Note'
        content = request.form.get('content', '')
        is_favorite = 1 if request.form.get('is_favorite') else 0
        
        db.execute('''
            UPDATE notes
            SET title = ?, content = ?, is_favorite = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (title, content, is_favorite, note_id))
        db.commit()
        
        flash('Note updated!', 'success')
        return redirect(url_for('subject_detail', subject_id=note['subject_id']))

    return render_template('editor.html', note=note, subject=subject)


@app.route('/note/delete/<int:note_id>', methods=['POST', 'GET'])
def delete_note(note_id):
    """Deletes an existing note."""
    db = get_db()
    note = db.execute('SELECT subject_id FROM notes WHERE id = ?', (note_id,)).fetchone()
    
    if note:
        subject_id = note['subject_id']
        db.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        db.commit()
        flash('Note deleted.', 'info')
        return redirect(url_for('subject_detail', subject_id=subject_id))
    
    return redirect(url_for('index'))


@app.route('/note/favorite/<int:note_id>', methods=['POST', 'GET'])
def toggle_favorite(note_id):
    """Toggles favorite status for a note."""
    db = get_db()
    db.execute('UPDATE notes SET is_favorite = 1 - is_favorite WHERE id = ?', (note_id,))
    db.commit()
    
    # Redirect back to where the user came from or to Home
    referrer = request.referrer or url_for('index')
    return redirect(referrer)


@app.route('/search')
def search():
    """Searches notes by title and content."""
    query = request.args.get('q', '').strip()
    notes = []
    if query:
        db = get_db()
        search_pattern = f'%{query}%'
        notes = db.execute('''
            SELECT n.id, n.title, n.content, n.is_favorite, n.updated_at, s.name AS subject_name, n.subject_id
            FROM notes n
            JOIN subjects s ON n.subject_id = s.id
            WHERE n.title LIKE ? OR n.content LIKE ?
            ORDER BY n.updated_at DESC
        ''', (search_pattern, search_pattern)).fetchall()

    return render_template('search.html', query=query, notes=notes)


@app.route('/settings')
def settings():
    """Renders application settings."""
    return render_template('settings.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
