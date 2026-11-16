## Pull Request: [PR-DOCS] [DOCS] Comprehensive Project README
**Source Branch:** `docs/readme-overview` -> **Target Branch:** `main`

### 1. Objective & Scope Alignment
- **OmniShelf Objective Addressed:** Project Documentation & Onboarding
- **Micro-Task Summary:** Added a detailed `README.md` documenting OmniShelf's purpose, zero-scraping pointer architecture, tech stack, repository structure, implemented features (Phases 0–2), local setup/test commands, and roadmap.

### 2. Technical Changes
- **Models/Migrations:** None.
- **Views/URLs/HTMX Endpoints:** None.
- **Templates/UI (`modern-web-guidance`):** None.
- **Documentation:** `README.md`.

### 3. Guardrail & Limitation Checklist
- [x] Zero story text/image scraping or copyright caching introduced.
- [x] Strict `request.user` tenancy isolation enforced on all queries.
- [x] All unit tests pass (`python manage.py test`).
