## Pull Request: [PR-3.2] [FEAT] Metadata Customization Engine (Aliases & Custom Covers)
**Source Branch:** `feat/3.2-metadata-customization-crud` -> **Target Branch:** `main`

### 1. Objective & Scope Alignment
- **OmniShelf Objective Addressed:** Metadata Customization & Zero-Reload Story Management
- **Micro-Task Summary:** Built HTMX-powered modal workflows (`LibraryEntryCreateView`, `LibraryEntryUpdateView`, `LibraryEntryDeleteView`) allowing users to add stories, override generic site titles with clean custom aliases, upload custom cover art or paste high-res cover URLs, assign folders/tags, and record anti-amnesia context notes without full-page reloads.

### 2. Technical Changes
- **Models/Migrations:** None (reuses `LibraryEntry` and creates initial `ReadingSnapshot` on story creation).
- **Views/URLs/HTMX Endpoints:** Created `library/forms.py` (`LibraryEntryForm` with user-scoped folder/tag querysets); added `LibraryEntryCreateView`, `LibraryEntryUpdateView`, and `LibraryEntryDeleteView` in `library/views.py` with OOB stats refresh and `HX-Trigger` modal/toast events; added routes `entries/new/`, `entries/<uuid:pk>/edit/`, and `entries/<uuid:pk>/delete/` in `library/urls.py`.
- **Templates/UI (`modern-web-guidance`):** Added shared native `<dialog id="omnishelf-modal">` with `closedby="any"` fallback in `templates/base.html`; created `stats_strip.html`, `entry_form_modal.html`, `entry_delete_modal.html` (with safe `autofocus` on Keep Story), plus progressive-enhancement full-page fallbacks; updated `dashboard.html`, `entry_grid.html`, and `entry_card.html` with Add/Edit/Delete controls.

### 3. Guardrail & Limitation Checklist
- [x] Zero story text/image scraping or copyright caching introduced.
- [x] Strict `request.user` tenancy isolation enforced on all queries and form foreign-key querysets.
- [x] All unit tests pass (`python manage.py test` — 21 tests OK).
