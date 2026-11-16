## Pull Request: [PR-0.1] [CHORE] Project Scaffolding & Modern Web Guidance Integration
**Source Branch:** `chore/0.1-init-and-web-guidance` -> **Target Branch:** `main`

### 1. Objective & Scope Alignment
- **OmniShelf Objective Addressed:** Foundation & Agent Skill Setup
- **Micro-Task Summary:** Initialized Python virtual environment, created `requirements.txt`, verified `modern-web-guidance` skill availability, scaffolded Django project `omnishelf_core` and core apps (`accounts`, `library`, `reader`), and configured `django-htmx`, `templates/`, `static/`, and `media/` settings.

### 2. Technical Changes
- **Models/Migrations:** None (initial app scaffolding).
- **Views/URLs/HTMX Endpoints:** Default `omnishelf_core/urls.py` generated.
- **Templates/UI (`modern-web-guidance`):** Created `templates/` and `static/` base directories; verified `modern-web-guidance` CLI search.

### 3. Guardrail & Limitation Checklist
- [x] Zero story text/image scraping or copyright caching introduced.
- [x] Strict `request.user` tenancy isolation enforced on all queries (N/A for scaffold).
- [x] `python manage.py check` passes with 0 issues.
