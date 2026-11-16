# OmniShelf

**OmniShelf** is a unified, distraction-free progress-tracking interface for serialized digital literature (web novels, translated serials, and multi-platform fiction). It acts as a **stateful URI pointer and metadata manager** so readers can organize their cross-platform reading lists and resume exact chapters without losing context.

---

## Architectural & Legal Principles

1. **Zero-Scraping / Non-Intrusive Pointer Architecture**  
   OmniShelf never downloads, scrapes, or caches copyrighted story text or chapter images. It stores only user-curated metadata, personal notes, and chapter URIs.
2. **Strict User Tenancy Isolation**  
   All folders, tags, library entries, and reading snapshots are scoped to the authenticated user (`CustomUser` with UUID primary key).
3. **Data Sovereignty**  
   Users can export their entire library metadata and URI history as a portable, timestamped `omnishelf_backup_v1` JSON snapshot and restore it idempotently without duplicating records.
4. **Calm Dark-Mode-First UI**  
   Designed with `color-scheme: dark` and accessible HTML form/navigation patterns to reduce UI fatigue during long reading sessions.

---

## Tech Stack

- **Backend:** Python 3.12+, Django (`>=5.0`, tested on Django 6.1.3)
- **Frontend:** Django Templates, **HTMX 2.0**, **Alpine.js 3.x**, **Tailwind CSS**
- **Database:** SQLite3 (local development)
- **Media & Utilities:** Pillow, `python-dotenv`, `django-htmx`

---

## Project Structure

```text
Omnishelf/
├── omnishelf_core/          # Django project settings, URLs, WSGI/ASGI
├── accounts/                # UUID-backed CustomUser, auth views, JSON backup/restore
│   ├── backup.py            # Portable omnishelf_backup_v1 export & idempotent import
│   ├── forms.py             # Accessible login & registration forms
│   ├── models.py            # CustomUser (UUID primary key)
│   ├── urls.py              # /accounts/login, register, logout, settings, export, import
│   └── views.py             # Auth & Data Sovereignty views
├── library/                 # Core domain models & Grand Library views
│   ├── models.py            # ReadingStatus, Folder, Tag, LibraryEntry, ReadingSnapshot
│   ├── admin.py             # Django Admin registrations
│   └── views.py             # Root landing / dashboard shell view
├── reader/                  # Sandboxed viewport & State-Capture reader app
├── templates/               # Base dark-mode shell & app templates
│   ├── base.html            # Responsive nav, HTMX CSRF headers, live toast region
│   ├── accounts/            # login.html, register.html, settings.html
│   └── library/             # home.html
├── .github/pr_logs/         # Micro-task Pull Request documentation logs
└── requirements.txt         # Python dependencies
```

---

## Implemented Features (Current State)

- **Phase 0 — Foundation & UI Shell (`PR-0.1`, `PR-0.2`):**
  - Django project scaffold (`omnishelf_core`, `accounts`, `library`, `reader`) with `django-htmx` and `python-dotenv`.
  - Dark-mode base template (`templates/base.html`) with responsive desktop/mobile navigation, skip-to-content accessibility link, and live toast notifications.
- **Phase 1 — Data Sovereignty & Authentication (`PR-1.1`, `PR-1.2`):**
  - UUID-backed `CustomUser` model.
  - Encapsulated Registration, Login, and POST-only Logout workflows with password visibility toggles and autofill attributes.
  - `/accounts/settings/` Data Sovereignty center with `omnishelf_backup_v1` JSON export (`/accounts/export/`) and duplicate-safe import (`/accounts/import/`).
- **Phase 2 — Core Domain Models & Taxonomy (`PR-2.1`, `PR-2.2`):**
  - `ReadingStatus` (`ACTIVE`, `ON_HOLD`, `BINGE_READY`, `HIATUS`, `COMPLETED`).
  - User-scoped `Folder` and `Tag` models with per-user uniqueness constraints and auto-slugification.
  - `LibraryEntry` with custom title/cover overrides, `current_uri`, automatic `source_domain` parsing on save, notes, and `ReadingSnapshot` immutable URI history.

---

## Local Setup & Running Tests

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py migrate

# 4. Run the test suite
python manage.py test

# 5. Start the development server
python manage.py runserver
```

---

## Roadmap (Remaining Phases)

- **Phase 3:** Grand Library visual card grid & HTMX metadata customization modals
- **Phase 4:** Dynamic taxonomy sidebar CRUD & real-time HTMX Omni-Search
- **Phase 5:** Sandboxed `<iframe>` viewport reader, Deep-Link Resume, & Freeze Snapshot controls
- **Phase 6:** Session-start UX telemetry & end-to-end integration QA
