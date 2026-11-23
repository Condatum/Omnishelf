## Pull Request: [PR-5.2] [FEAT] State-Capture ("Freeze Snapshot") Bookmarking & URI Rollback Drawer
**Source Branch:** `feat/5.2-state-capture-snapshot` -> **Target Branch:** `main`

### 1. Objective & Scope Alignment
- **OmniShelf Objective Addressed:** Reading State Persistence & Source Volatility Resilience
- **Micro-Task Summary:** Engineered the State-Capture (**Freeze Snapshot**) control bar in the Reader HUD and Quick Snapshot HTMX modal on Grand Library cards, featuring 1-click clipboard URI paste, a `+1 Chapter` smart regex increment helper (`"Ch. 41"` -> `"Ch. 42"`), instant confirmation badges, automatic `source_domain` re-evaluation, immutable `ReadingSnapshot` logging, and a collapsible **Snapshot History Drawer** with 1-click URI rollback.

### 2. Technical Changes
- **Models/Migrations:** None (persists immutable checkpoints in `ReadingSnapshot` and updates `LibraryEntry`).
- **Views/URLs/HTMX Endpoints:** Created `reader/utils.py` (`increment_chapter_label`), `reader/forms.py` (`FreezeSnapshotForm`), and added `freeze_snapshot_view`, `quick_snapshot_modal_view`, and `rollback_snapshot_view` in `reader/views.py` and `reader/urls.py`.
- **Templates/UI (`modern-web-guidance`):** Created `freeze_confirmation.html`, `snapshot_history_list.html`, `hud_oob_updates.html`, and `quick_snapshot_modal.html`; upgraded `templates/reader/viewport.html` with the Freeze Snapshot bar and collapsible Snapshot History Drawer; wired `entry_card.html`'s Update Snapshot button to the Quick Snapshot modal.

### 3. Guardrail & Limitation Checklist
- [x] Zero story text/image scraping or copyright caching introduced.
- [x] Strict `request.user` tenancy isolation enforced on all snapshot freeze, modal, and rollback routes.
- [x] All unit tests pass (`python manage.py test` — 32 tests OK).
