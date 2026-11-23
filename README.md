# OmniShelf

**OmniShelf** is a unified, distraction-free progress-tracking interface for serialized digital literature (web novels, translated serials, fanfiction, and multi-platform fiction). It operates strictly as a **stateful URI pointer and metadata manager**, enabling readers to organize cross-platform shelves, customize titles and cover art, launch chapters in one click, and freeze immutable chapter URI checkpoints without losing reading context.

---

## Legal & Architectural Compliance Statement

1. **Non-Intrusive Pointer Architecture (Zero Scraping / Zero Caching)**  
   OmniShelf never uses scrapers (`BeautifulSoup`, `Scrapy`), headless crawlers, or background workers to download, store, or cache copyrighted story prose or chapter images. It persists only user-supplied metadata, personal context notes, and active/historical chapter URIs.
2. **Respectful Viewport Framing & External Tab Fallback**  
   The integrated reader uses a standard browser-sandboxed `<iframe>` (`sandbox="allow-scripts allow-same-origin allow-forms allow-popups"`) and **never** proxies or strips `X-Frame-Options` / `CSP` security headers. When publishers block framing or enforce Cloudflare anti-bot checks, the Reader HUD provides a 1-click **External Tab Fallback** alongside manual **Freeze Snapshot** state capture.
3. **Strict User Tenancy Isolation**  
   Every `Folder`, `Tag`, `LibraryEntry`, `ReadingSnapshot`, and personal `UsabilityMetric` record is strictly scoped to `request.user` (`CustomUser` with UUID primary key). Cross-tenant reads or mutations return `404`.
4. **Data Sovereignty**  
   Users can export their entire library metadata and `ReadingSnapshot` URI history as a portable, timestamped `omnishelf_backup_v1` JSON snapshot and restore it idempotently on any device without duplicating records.
5. **Solo Utility Scope**  
   OmniShelf is intentionally focused as a private, low-friction personal reading utility — no public profiles, comment threads, or social feeds.

---

## Tech Stack

- **Backend:** Python 3.12+, Django (`>=5.0`, verified on Django 6.1.3)
- **Frontend:** Django Templates, **HTMX 2.0.4** (SRI-pinned), **Alpine.js 3.14.8** (SRI-pinned), **Tailwind CSS** (dark-mode-first design tokens governed by `modern-web-guidance`)
- **Database:** SQLite3 (local development) / PostgreSQL-ready
- **Media & Utilities:** Pillow (custom cover uploads), `python-dotenv`, `django-htmx`

---

## Project Structure

```text
Omnishelf/
├── omnishelf_core/          # Django settings, root URLs, WSGI/ASGI
├── accounts/                # UUID-backed CustomUser, auth views, JSON Data Sovereignty backup/restore
│   ├── backup.py            # Portable omnishelf_backup_v1 export & idempotent import
│   ├── forms.py             # Accessible sign-in & registration forms
│   ├── models.py            # CustomUser (UUID primary key)
│   └── views.py             # Auth & Data Sovereignty views
├── library/                 # Domain models, Grand Library dashboard, Taxonomy, Omni-Search, UX Telemetry
│   ├── models.py            # ReadingStatus, Folder, Tag, LibraryEntry, ReadingSnapshot, UsabilityMetric
│   ├── forms.py             # User-scoped LibraryEntryForm, FolderForm, TagForm, UsabilityFeedbackForm
│   ├── views.py             # GrandLibraryView, HTMX CRUD modals, Sidebar CRUD, Omni-Search, /ux-metrics/
│   └── tests.py             # Model, Dashboard, CRUD, Taxonomy, Search, Telemetry & E2E Integration tests
├── reader/                  # Sandboxed Viewport Reader & State-Capture ("Freeze Snapshot") engine
│   ├── utils.py             # Smart chapter label regex incrementer ("Ch. 41" -> "Ch. 42")
│   ├── forms.py             # FreezeSnapshotForm
│   ├── views.py             # ViewportReaderView, Freeze Snapshot, Quick Card Modal, URI Rollback
│   └── tests.py             # Viewport, last_read_at, Snapshot, Smart Increment & Rollback tests
├── templates/               # Modern-web-guidance compliant dark-mode templates & HTMX partials
│   ├── base.html            # Responsive nav, native <dialog>, SRI scripts, toast live region
│   ├── accounts/            # login.html, register.html, settings.html
│   ├── library/             # dashboard.html, ux_metrics.html, partials/ (cards, modals, sidebar, search)
│   └── reader/              # viewport.html, partials/ (HUD OOB updates, history drawer, quick modal)
├── .github/pr_logs/         # Structured micro-task PR documentation artifacts (PR-0.1 .. PR-6.2)
└── requirements.txt         # Python dependencies
```

---

## Completed Feature Phases & Micro-Chunk Git History

| PR Log | Branch | Milestone / Deliverable |
| :--- | :--- | :--- |
| `PR-0.1` | `chore/0.1-init-and-web-guidance` | Django 5.x scaffold (`accounts`, `library`, `reader`) & `modern-web-guidance` integration |
| `PR-0.2` | `feat/0.2-base-ui-shell` | Responsive dark-mode base shell, HTMX CSRF headers, Alpine.js & toast live region |
| `PR-1.1` | `feat/1.1-encapsulated-auth` | UUID-backed `CustomUser` and encapsulated Register/Login/POST-Logout workflows |
| `PR-1.2` | `feat/1.2-data-sovereignty-sync` | Portable `omnishelf_backup_v1` JSON export & duplicate-safe import |
| `PR-2.1` | `feat/2.1-taxonomy-models` | User-scoped `Folder`, `Tag`, and `ReadingStatus` multi-tier taxonomy schema |
| `PR-2.2` | `feat/2.2-library-and-snapshot-models` | `LibraryEntry` (auto `source_domain`, cover/title overrides) & immutable `ReadingSnapshot` |
| `PR-3.1` | `feat/3.1-grand-library-grid` | Grand Library responsive visual card grid, cover fallbacks, progress & domain badges |
| `PR-3.2` | `feat/3.2-metadata-customization-crud` | Native `<dialog>` HTMX modals for custom aliases, cover uploads, and full CRUD |
| `PR-4.1` | `feat/4.1-taxonomy-sidebar-crud` | Interactive HTMX Folder/Tag sidebar CRUD & quick ReadingStatus filter tabs |
| `PR-4.2` | `feat/4.2-omni-search` | Debounced HTMX Omni-Search across titles, tags, source domains, and notes |
| `PR-5.1` | `feat/5.1-sandboxed-viewport-reader` | Sandboxed `<iframe>` reader HUD, Deep-Link Resume launcher, and X-Frame fallback |
| `PR-5.2` | `feat/5.2-state-capture-snapshot` | Freeze Snapshot tool, clipboard paste, `+1 Chapter` smart bump, and URI Rollback drawer |
| `PR-6.1` | `feat/6.1-ux-validation-telemetry` | Session-start latency tracker, Usability Feedback modal, and `/ux-metrics/` 60%+ dashboard |
| `PR-6.2` | `chore/6.2-e2e-tests-and-docs` | Full-lifecycle E2E integration tests, `modern-web-guidance` accessibility audit, and docs |

---

## Local Setup & Verification

```bash
# 1. Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py migrate

# 4. Run full automated test suite (accounts, library, reader, and E2E integration)
python manage.py test

# 5. Verify Django system checks and modern-web-guidance static scan
python manage.py check
npx modern-web-guidance@latest legacy-scan templates/

# 6. Start the development server
python manage.py runserver
```
