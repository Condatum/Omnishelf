## Pull Request: [PR-4.1] [FEAT] Dynamic Taxonomy Management UI
**Source Branch:** `feat/4.1-taxonomy-sidebar-crud` -> **Target Branch:** `main`

### 1. Objective & Scope Alignment
- **OmniShelf Objective Addressed:** Flexible Taxonomy (Folders, Tags, & Reading Statuses)
- **Micro-Task Summary:** Implemented an interactive HTMX taxonomy sidebar for creating, renaming, and deleting user-scoped `Folder` and `Tag` items inline, alongside quick reading-status filter tabs (`All`, `Active`, `Binge-Ready`, `On Hold`, `Hiatus`, `Completed`) that combine seamlessly with folder and tag filters.

### 2. Technical Changes
- **Models/Migrations:** None (reuses user-scoped `Folder`, `Tag`, and `ReadingStatus` models).
- **Views/URLs/HTMX Endpoints:** Added `FolderForm` and `TagForm` in `library/forms.py`; added HTMX endpoints `folder_create_view`, `folder_rename_view`, `folder_delete_view`, `tag_create_view`, `tag_rename_view`, and `tag_delete_view` plus multi-facet filtering in `GrandLibraryView` (`library/views.py`, `library/urls.py`).
- **Templates/UI (`modern-web-guidance`):** Created `taxonomy_sidebar.html` (with accessible inline rename/create forms, counts, and mobile toggle) and `status_tabs.html`; updated `dashboard.html` with a responsive two-column workspace and `entry_grid.html` with active filter pills and filtered-empty state.

### 3. Guardrail & Limitation Checklist
- [x] Zero story text/image scraping or copyright caching introduced.
- [x] Strict `request.user` tenancy isolation enforced on all queries and taxonomy mutations.
- [x] All unit tests pass (`python manage.py test` — 24 tests OK).
