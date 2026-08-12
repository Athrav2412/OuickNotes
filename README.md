# QuickNotes 📝

QuickNotes is a clean, minimal, mobile-first note-taking web application built with Python **Flask** and **SQLite**. It offers zero-friction subject organization, instant note creation, favorite bookmarking, and local preference storage.

---

## Features

- **Subject Management**: Categorize notes under custom subjects with note counters.
- **Distraction-Free Editor**: Clean text editor for rapid note creation and editing.
- **Favorites**: Toggle key notes as favorites for quick visibility.
- **Search**: Server-side keyword search across titles and note contents.
- **Dark Mode**: Built-in dark mode toggle saved in client `localStorage`.
- **Custom Font Sizes**: Switch between Small, Medium, and Large reading sizes.
- **Responsive Layout**: Mobile-first design tailored for phone screens and desktop browsers.

---

## Tech Stack

- **Backend**: Python 3.x, Flask
- **Database**: SQLite3 (native standard library)
- **Frontend**: HTML5, Jinja2 Templates, Vanilla CSS3 (Variables), Vanilla JS (ES6)
- **Deployment**: WSGI-compatible with `gunicorn` for Render deployment

---

## Project Structure

```text
QuickNotes/
├── app.py                  # Main Flask server application & SQLite database layer
├── requirements.txt        # Minimal Python dependencies
├── quicknotes.db           # SQLite database file (created automatically)
├── templates/              # Jinja2 HTML Templates
│   ├── index.html          # Home page
│   ├── subjects.html       # Subjects overview & creation
│   ├── notes.html          # Notes under selected subject
│   ├── editor.html         # Note editor & view
│   ├── search.html         # Search results page
│   └── settings.html       # Appearance & info settings
└── static/
    ├── css/
    │   └── style.css       # Clean, modern stylesheet
    └── js/
        └── app.js          # Theme, font-size, and UI handlers
