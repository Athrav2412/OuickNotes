/**
 * QuickNotes JavaScript Functionality
 * Handles theme toggling, font sizing, dynamic modals, and confirmation alerts.
 */

document.addEventListener('DOMContentLoaded', () => {
    initDarkMode();
    initFontSize();
    initDeleteConfirmations();
    initSubjectModal();
});

/* -------------------------------------------------------------------
   1. Dark Mode Persistence
   ------------------------------------------------------------------- */
function initDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const savedTheme = localStorage.getItem('qn_theme');

    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        if (darkModeToggle) darkModeToggle.checked = true;
    } else if (savedTheme === 'light') {
        document.body.classList.remove('dark-mode');
        if (darkModeToggle) darkModeToggle.checked = false;
    }

    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', (e) => {
            if (e.target.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('qn_theme', 'dark');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('qn_theme', 'light');
            }
        });
    }
}

/* -------------------------------------------------------------------
   2. Font Size Option
   ------------------------------------------------------------------- */
function initFontSize() {
    const fontBtns = document.querySelectorAll('.font-btn');
    const savedFontSize = localStorage.getItem('qn_font_size') || 'medium';

    applyFontSize(savedFontSize);

    fontBtns.forEach((btn) => {
        if (btn.dataset.size === savedFontSize) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }

        btn.addEventListener('click', () => {
            const size = btn.dataset.size;
            applyFontSize(size);
            localStorage.setItem('qn_font_size', size);

            fontBtns.forEach((b) => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
}

function applyFontSize(size) {
    document.body.classList.remove('font-small', 'font-medium', 'font-large');
    document.body.classList.add(`font-${size}`);
}

/* -------------------------------------------------------------------
   3. Delete Confirmations
   ------------------------------------------------------------------- */
function initDeleteConfirmations() {
    const deleteButtons = document.querySelectorAll('.delete-confirm');

    deleteButtons.forEach((btn) => {
        btn.addEventListener('click', (e) => {
            const customMessage = btn.getAttribute('data-confirm') || 'Are you sure you want to delete this item?';
            if (!confirm(customMessage)) {
                e.preventDefault();
            }
        });
    });
}

/* -------------------------------------------------------------------
   4. Subject Modal Handler
   ------------------------------------------------------------------- */
function initSubjectModal() {
    const openBtn = document.getElementById('openSubjectModal');
    const closeBtn = document.getElementById('closeSubjectModal');
    const modal = document.getElementById('subjectModal');

    if (openBtn && modal) {
        openBtn.addEventListener('click', () => {
            modal.classList.add('show');
            const input = modal.querySelector('input');
            if (input) input.focus();
        });
    }

    if (closeBtn && modal) {
        closeBtn.addEventListener('click', () => {
            modal.classList.remove('show');
        });
    }

    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('show');
            }
        });
    }
}
