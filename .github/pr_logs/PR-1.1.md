## Pull Request: [PR-1.1] [FEAT] Encapsulated Registration & Login System
**Source Branch:** `feat/1.1-encapsulated-auth` -> **Target Branch:** `main`

### 1. Objective & Scope Alignment
- **OmniShelf Objective Addressed:** Data Sovereignty & Encapsulated Authentication
- **Micro-Task Summary:** Implemented UUID-backed `CustomUser` model (`accounts/models.py`), `OmniShelfUserCreationForm` & `OmniShelfAuthenticationForm` with accessible autofill attributes and password visibility toggles, and `register_view`, `login_view`, `logout_view` (POST-only).

### 2. Technical Changes
- **Models/Migrations:** `accounts/models.py` (`CustomUser` with `UUIDField` PK), `accounts/migrations/0001_initial.py`, `AUTH_USER_MODEL = 'accounts.CustomUser'`.
- **Views/URLs/HTMX Endpoints:** `accounts/views.py`, `accounts/urls.py` (`login`, `register`, `logout`).
- **Templates/UI (`modern-web-guidance`):** `templates/accounts/login.html`, `templates/accounts/register.html` with `autocomplete="username"`, `autocomplete="current-password"`, `autocomplete="new-password"`, `spellcheck="false"`, and Alpine.js password visibility toggle.

### 3. Guardrail & Limitation Checklist
- [x] Zero story text/image scraping or copyright caching introduced.
- [x] Strict `request.user` tenancy isolation enforced on all queries.
- [x] All unit tests pass (`python manage.py test` — 6 tests OK).
