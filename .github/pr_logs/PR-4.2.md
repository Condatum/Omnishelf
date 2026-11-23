## Pull Request: [PR-4.2] [FEAT] Global Omni-Search Engine
**Source Branch:** `feat/4.2-omni-search` -> **Target Branch:** `main`

### 1. Objective & Scope Alignment
- **OmniShelf Objective Addressed:** Instant Multi-Field Discovery & Unified Search
- **Micro-Task Summary:** Implemented a debounced HTMX global Omni-Search bar (`hx-trigger="keyup changed delay:200ms, search"`) querying `custom_title`, `original_source_title`, `tags__name`, `source_domain`, and `notes` with multi-term `Q` filtering and `.distinct()` results, seamlessly combined with active Folder, Tag, and ReadingStatus filters.

### 2. Technical Changes
- **Models/Migrations:** None.
- **Views/URLs/HTMX Endpoints:** Added `omni_search_view` (`/library/search/`, `library:omni_search`) and multi-term `Q` filtering in `_get_user_library_context` (`library/views.py`, `library/urls.py`) with OOB synchronization across grid, status tabs, sidebar, and hidden search filter inputs.
- **Templates/UI (`modern-web-guidance`):** Created semantic `<search>` component in `omni_search_bar.html` with IME-safe Enter handling (`isComposing || keyCode === 229`), `autocorrect="off"`, loading indicator, and `omni_search_hidden_filters.html`; updated `dashboard.html`, `status_tabs.html`, `taxonomy_sidebar.html`, and `entry_grid.html` to preserve active search queries across filter transitions.

### 3. Guardrail & Limitation Checklist
- [x] Zero story text/image scraping or copyright caching introduced.
- [x] Strict `request.user` tenancy isolation enforced on all queries.
- [x] All unit tests pass (`python manage.py test` — 26 tests OK).
