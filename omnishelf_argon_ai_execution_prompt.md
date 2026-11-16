# SYSTEM DIRECTIVE: OMNISHELF AUTONOMOUS DEVELOPMENT BLUEPRINT
**Target Agent:** Antigravity Argon AI  
**Project Name:** OmniShelf – A Unified Progress-Tracking Interface for Serialized Digital Literature  
**Core Framework:** Python Django 5.x (Full-Stack / HTMX / Alpine.js / Tailwind CSS)  
**Agent Skill Dependency:** `npx modern-web-guidance@latest install`  

---

## 1. AGENT PERSONA & OPERATIONAL PROTOCOL

You are an elite, autonomous Principal Full-Stack Django Architect and DevOps Engineer operating inside the **Antigravity (Argon)** IDE environment. Your objective is to plan, architect, and execute the end-to-end development of **OmniShelf**. 

### Mandatory Execution Rules:
1. **Skill Initialization First:** Before writing any application or UI code, you MUST execute `npx modern-web-guidance@latest install` in the project root to inject modern web styling, accessibility, responsive layout patterns, and interactive component guidelines into your workspace context.
2. **Micro-Chunked Git Flow:** You are strictly forbidden from building monolithically on the `main` branch. For **every single micro-task** defined in Section 4:
   - Checkout a new feature/task branch from `main` (or `develop`) using the exact naming convention specified.
   - Implement **only** the scope of that micro-task.
   - Write and run unit/integration tests (`python manage.py test`) to verify zero regressions.
   - Stage and commit using the exact **Conventional Commit** message provided.
   - Generate a structured **Pull Request (PR) Documentation artifact** (in `.github/pr_logs/PR-<Task-ID>.md` or via CLI) before merging back into `main` with `--no-ff`.
3. **Strict Architectural Boundaries (Legal & Technical Limitations):**
   - **Zero Scraping/Caching:** Never implement `BeautifulSoup`, `Scrapy`, or background workers that download, store, or cache story text or copyrighted chapter images. OmniShelf is strictly a **stateful URI pointer and metadata manager**.
   - **Manual Snapshot Progression:** Do not attempt to bypass cross-origin (`CORS` / `X-Frame-Options`) security inside the sandboxed `<iframe>` via illegal proxy stripping. Provide clean manual URI input/paste-and-freeze workflows alongside the integrated viewport and a 1-click "External Browser Fallback" when sites block framing.
   - **Solo Utility Scope:** Do not build public profiles, comment threads, or social sharing modules.

---

## 2. TECHNICAL STACK & ARCHITECTURE SPECIFICATIONS

* **Backend:** Python 3.12+, Django 5.x
* **Database:** SQLite3 (Local Development) / PostgreSQL-ready via `dj-database-url` (Cloud Sovereignty)
* **Frontend Paradigm:** Django Templates enhanced with **HTMX** (for zero-reload modal updates, Snapshot freezing, and Omni-Search filtering), **Alpine.js** (for client-side viewport controls and sidebar toggles), and **Tailwind CSS** (governed by `npx modern-web-guidance@latest install`).
* **Media Handling:** Pillow for custom cover art uploads + URL fallback support for external cover links.
* **Security:** Django built-in Authentication (`django.contrib.auth`), CSRF protection on all HTMX requests, user-scoped QuerySet isolation (`request.user` ownership enforcement on every view).

---

## 3. PROJECT TIMELINE & ESSENTIAL FEATURE MILESTONES

| Phase | Milestone Name | Target Duration | Core Deliverables |
| :--- | :--- | :--- | :--- |
| **Phase 0** | **Foundation & Agent Skill Setup** | Days 1–2 | Git init, virtual environment, Django scaffold, `modern-web-guidance` installation, base layout shell. |
| **Phase 1** | **Data Sovereignty & Auth Engine** | Days 3–5 | Custom User model, encapsulated Login/Registration/Logout views, user-isolated security middleware, cloud-sync export/import JSON utility. |
| **Phase 2** | **Core Domain Models & Taxonomy** | Days 6–8 | `Folder`, `Tag`, `LibraryEntry`, and `ReadingSnapshot` models; custom title/cover overrides; multi-tier status taxonomy ("Active", "On Hold", "Binge-Ready", "Hiatus"). |
| **Phase 3** | **The "Grand Library" Dashboard** | Days 9–12 | Visual responsive grid, customizable cover cards, progress badge indicators, CRUD modals for entries and metadata overrides. |
| **Phase 4** | **Omni-Search & Dynamic Taxonomy UI** | Days 13–15 | Real-time HTMX global search bar (filtering by alias, tag, status, or source domain), sidebar folder/tag navigation. |
| **Phase 5** | **Sandboxed Viewport & Deep-Link Resume** | Days 16–19 | "Deep-Link" primary launch action, integrated sandboxed `<iframe>` reader view, top HUD control bar, "Freeze Snapshot" state-capture mechanism, X-Frame fallback detector. |
| **Phase 6** | **UX Validation Telemetry & QA Polish** | Days 20–21 | Session-start time tracker (measuring seconds from login to chapter launch for the 60% High Utility rubric), comprehensive test suite, production readiness. |

---

## 4. MICRO-CHUNKED EXECUTION PLAN (BRANCH -> COMMIT -> PR -> MERGE)

Execute the following tasks sequentially. Do not skip steps.

---

### PHASE 0: FOUNDATION & MODERN WEB GUIDANCE SETUP

#### Task 0.1: Repository Initialization & Modern Web Skill Injection
* **Branch:** `chore/0.1-init-and-web-guidance`
* **Action Items:**
  1. Initialize Git repository and create `.gitignore` (Python, Django, Node, `.env`, `media/`, `db.sqlite3`).
  2. Run `npx modern-web-guidance@latest install` and verify skill rules are loaded into the workspace.
  3. Create `requirements.txt` (`Django>=5.0`, `Pillow`, `python-dotenv`, `django-htmx`).
  4. Initialize Django project `omnishelf_core` and main apps: `accounts`, `library`, `reader`.
* **Commit Message:**
  ```text
  chore(setup): initialize django project and install modern-web-guidance skill
  ```
* **PR Documentation (`PR-0.1`):**
  * **Title:** `[CHORE] Project Scaffolding & Modern Web Guidance Integration`
  * **Summary:** Sets up the foundational Django 5.x directory structure, core apps (`accounts`, `library`, `reader`), and installs `modern-web-guidance` for UI/UX compliance.
  * **Verification:** `python manage.py check` passes with 0 issues.

#### Task 0.2: Base Design System & App Shell
* **Branch:** `feat/0.2-base-ui-shell`
* **Action Items:**
  1. Create `templates/base.html` following the design tokens and typography rules from `modern-web-guidance` (dark-mode optimized to prevent UI Fatigue).
  2. Include HTMX, Alpine.js, and Tailwind CSS setup.
  3. Build a distraction-free responsive navigation shell with toast notification support for HTMX events.
* **Commit Message:**
  ```text
  feat(ui): implement responsive dark-mode base shell with HTMX and Alpine.js
  ```
* **PR Documentation (`PR-0.2`):**
  * **Title:** `[FEAT] Unified Base Template & Low-Friction UI Shell`
  * **Summary:** Addresses the "UI Fatigue" pain point by establishing a consistent, calm, dark-mode-first reading management interface.
  * **Verification:** Render root health-check view and verify responsive navigation breakpoints.

---

### PHASE 1: DATA SOVEREIGNTY & ENCAPSULATED AUTHENTICATION

#### Task 1.1: Custom User Model & Authentication Views
* **Branch:** `feat/1.1-encapsulated-auth`
* **Action Items:**
  1. Create `CustomUser` model in `accounts/models.py` (extending `AbstractUser` with `uuid` primary key for cloud-sync safety).
  2. Build encapsulated Registration, Login, and Logout views and forms in `accounts/`.
  3. Apply `modern-web-guidance` form styling with clear validation feedback.
* **Commit Message:**
  ```text
  feat(auth): implement UUID-backed CustomUser and encapsulated auth workflows
  ```
* **PR Documentation (`PR-1.1`):**
  * **Title:** `[FEAT] Encapsulated Registration & Login System`
  * **Summary:** Delivers private, credential-based access so reading libraries persist securely across sessions.
  * **Verification:** Run unit tests for user signup, login redirect, logout, and unauthenticated route blocking.

#### Task 1.2: Data Sovereignty Cloud Backup & Restore Utility
* **Branch:** `feat/1.2-data-sovereignty-sync`
* **Action Items:**
  1. Create an account settings endpoint allowing users to export their entire library metadata and URI history as a portable, timestamped JSON snapshot.
  2. Create a JSON import parser that restores library state safely without duplicating records.
* **Commit Message:**
  ```text
  feat(accounts): add JSON library export and import for user data sovereignty
  ```
* **PR Documentation (`PR-1.2`):**
  * **Title:** `[FEAT] Data Sovereignty Portable Backup & Sync Engine`
  * **Summary:** Protects users against device failure by enabling full cloud-ready JSON serialization and restoration of reading history.
  * **Verification:** Test export and re-import cycle via `accounts/tests.py`.

---

### PHASE 2: CORE DOMAIN MODELS & FLEXIBLE TAXONOMY

#### Task 2.1: Taxonomy Models (Folders, Tags, & Reading Statuses)
* **Branch:** `feat/2.1-taxonomy-models`
* **Action Items:**
  1. In `library/models.py`, create `Folder` (user-scoped, name, icon/color, sort order) and `Tag` (user-scoped, name, slug, color_hex).
  2. Define `ReadingStatus` TextChoices: `ACTIVE` ("Active Reading"), `ON_HOLD` ("On Hold"), `BINGE_READY` ("Binge-Ready"), `HIATUS` ("Hiatus"), `COMPLETED` ("Completed").
* **Commit Message:**
  ```text
  feat(library): define user-scoped Folder, Tag, and ReadingStatus taxonomy models
  ```
* **PR Documentation (`PR-2.1`):**
  * **Title:** `[FEAT] Multi-Tier Taxonomy Models (Folders, Tags, Statuses)`
  * **Summary:** Establishes the database schema for the Flexible Taxonomy objective, allowing granular organization by genre, priority, or status.
  * **Verification:** Run migrations and model validation tests in `library/tests/test_models.py`.

#### Task 2.2: LibraryEntry & ReadingSnapshot URI Persistence Models
* **Branch:** `feat/2.2-library-and-snapshot-models`
* **Action Items:**
  1. Create `LibraryEntry` model in `library/models.py`:
     - `user` (ForeignKey)
     - `custom_title` (CharField - overrides generic site title)
     - `original_source_title` (CharField, optional)
     - `custom_cover_image` (ImageField, optional) & `custom_cover_url` (URLField, optional)
     - `current_uri` (URLField, max_length=2000 - the active Deep-Link bookmark)
     - `source_domain` (CharField - auto-extracted via `urllib.parse.urlparse` on save, e.g., `royalroad.com`, `reddit.com`)
     - `chapter_label` (CharField, e.g., `"Ch. 142"` or `"Arc 4 Pt 2"`)
     - `status` (ChoiceField using `ReadingStatus`)
     - `folder` (ForeignKey to `Folder`, null=True)
     - `tags` (ManyToManyField to `Tag`, blank=True)
     - `notes` (TextField - personal context reminder to prevent Contextual Amnesia)
     - `last_read_at` (DateTimeField)
  2. Create `ReadingSnapshot` model (audit history of saved URIs per `LibraryEntry` so if a URL structure changes or breaks, the user retains a historical trail of previous chapter URIs and timestamps).
* **Commit Message:**
  ```text
  feat(library): implement LibraryEntry metadata model and ReadingSnapshot URI history
  ```
* **PR Documentation (`PR-2.2`):**
  * **Title:** `[FEAT] LibraryEntry & ReadingSnapshot Persistence Schema`
  * **Summary:** Solves "Contextual Amnesia" and "Source Volatility" by storing the exact active URI, auto-parsed source domain, custom cover/title overrides, and an immutable history of prior chapter snapshots.
  * **Verification:** Verify automatic `source_domain` extraction on `.save()` and cascade rules via unit tests.

---

### PHASE 3: THE "GRAND LIBRARY" DASHBOARD & METADATA CUSTOMIZATION

#### Task 3.1: Grand Library Visual Grid & Progress Cards
* **Branch:** `feat/3.1-grand-library-grid`
* **Action Items:**
  1. Build `GrandLibraryView` in `library/views.py` scoped strictly to `request.user`.
  2. Design the responsive visual grid card component using `modern-web-guidance` card patterns:
     - High-aspect-ratio cover art display (with sleek fallback gradient if no cover is set).
     - Status badge ("Binge-Ready", "Active", etc.), `chapter_label` pill, and `source_domain` favicon/badge.
     - Primary **"Deep-Link Resume"** CTA button and quick **"Update Snapshot"** trigger.
* **Commit Message:**
  ```text
  feat(dashboard): build Grand Library visual grid and customizable story cards
  ```
* **PR Documentation (`PR-3.1`):**
  * **Title:** `[FEAT] The "Grand Library" Dashboard & Visual Card Grid`
  * **Summary:** Implements the main dashboard displaying active reads with custom aesthetics, chapter progress indicators, and source domain badges.
  * **Verification:** Test dashboard rendering with 0 entries (empty state onboarding) and 15+ entries.

#### Task 3.2: Metadata Customization & Story Creation HTMX Modals
* **Branch:** `feat/3.2-metadata-customization-crud`
* **Action Items:**
  1. Create HTMX-powered modal views for adding a new story (`LibraryEntryCreateView`) and overriding metadata (`LibraryEntryUpdateView`, `LibraryEntryDeleteView`).
  2. Allow users to set custom aliases (`custom_title`), upload custom cover art or paste high-res cover URLs, assign folders/tags, and record brief context notes (e.g., *"Stopped right before the tournament finals"*).
* **Commit Message:**
  ```text
  feat(library): add HTMX modals for custom title aliases, cover art overrides, and CRUD
  ```
* **PR Documentation (`PR-3.2`):**
  * **Title:** `[FEAT] Metadata Customization Engine (Aliases & Custom Covers)`
  * **Summary:** Empowers users to override ugly or generic blog/aggregator titles with clean custom aliases and high-resolution cover artwork without full-page reloads.
  * **Verification:** Verify CRUD permissions (users cannot edit another user's `LibraryEntry`) and cover upload rendering.

---

### PHASE 4: DYNAMIC TAXONOMY UI & OMNI-SEARCH ENGINE

#### Task 4.1: Dynamic Taxonomy Sidebar (Folder & Tag Management)
* **Branch:** `feat/4.1-taxonomy-sidebar-crud`
* **Action Items:**
  1. Implement HTMX endpoints to create, rename, and delete user `Folder` and `Tag` items directly from the dashboard sidebar.
  2. Add quick status-filter tabs across the top of the Grand Library (`All`, `Active`, `Binge-Ready`, `On Hold`, `Hiatus`, `Completed`).
* **Commit Message:**
  ```text
  feat(taxonomy): implement interactive sidebar for Folders, Tags, and Status tabs
  ```
* **PR Documentation (`PR-4.1`):**
  * **Title:** `[FEAT] Dynamic Taxonomy Management UI`
  * **Summary:** Provides a multi-tier organization sidebar for sorting serialized fiction by folder, custom tag, or reading priority.
  * **Verification:** Test filtering accuracy by Folder ID, Tag slug, and ReadingStatus enum.

#### Task 4.2: Real-Time Omni-Search Bar
* **Branch:** `feat/4.2-omni-search`
* **Action Items:**
  1. Implement an HTMX debounced global search endpoint (`hx-get`, `hx-trigger="keyup changed delay:200ms"`) querying `Q(custom_title__icontains) | Q(original_source_title__icontains) | Q(tags__name__icontains) | Q(source_domain__icontains) | Q(notes__icontains)`.
  2. Combine search queries seamlessly with active Folder/Status filters.
* **Commit Message:**
  ```text
  feat(search): implement debounced HTMX Omni-Search across titles, tags, and domains
  ```
* **PR Documentation (`PR-4.2`):**
  * **Title:** `[FEAT] Global Omni-Search Engine`
  * **Summary:** Allows instant filtering of the Grand Library by custom alias, tag name, context notes, or source domain (e.g., typing `reddit` or `novelupdates`).
  * **Verification:** Unit test complex multi-term `Q` object queries and distinct result sets.

---

### PHASE 5: SANDBOXED VIEWPORT, STATE-CAPTURE SNAPSHOT & DEEP-LINK RESUME

#### Task 5.1: Sandboxed Viewport & "Deep-Link" Resume Launcher
* **Branch:** `feat/5.1-sandboxed-viewport-reader`
* **Action Items:**
  1. In `reader/views.py`, build `ViewportReaderView` (`/reader/<uuid:entry_id>/`).
  2. Configure the primary **"Deep-Link Resume"** button on every Grand Library card to launch directly into this view (or optionally open a synchronized dual-tab experience), bypassing source site homepages and loading `entry.current_uri` immediately.
  3. Build the unified Reader HUD (Heads-Up Display) bar above a sandboxed `<iframe src="{{ entry.current_uri }}" sandbox="allow-scripts allow-same-origin allow-forms allow-popups">`.
  4. Include an instant **"External Tab Fallback"** button in the HUD for sites that enforce strict `X-Frame-Options: DENY` or aggressive Cloudflare anti-bot walls, ensuring zero dead-ends under the Source Compatibility limitation.
* **Commit Message:**
  ```text
  feat(reader): build integrated sandboxed viewport and Deep-Link Resume workflow
  ```
* **PR Documentation (`PR-5.1`):**
  * **Title:** `[FEAT] Contextual Resumption Viewport & Deep-Link Launcher`
  * **Summary:** Enables instant chapter resumption inside a unified OmniShelf HUD while providing graceful fallback handling for sites with anti-framing headers.
  * **Verification:** Verify `last_read_at` timestamp updates automatically upon launching a Deep-Link session.

#### Task 5.2: State-Capture ("Freeze Snapshot") Bookmark Tool
* **Branch:** `feat/5.2-state-capture-snapshot`
* **Action Items:**
  1. Inside the Reader HUD (and as a quick-action on the Library Card), build the **"Freeze Snapshot"** control bar.
  2. Allow the user to update their current URI (via 1-click clipboard paste or viewport URI input), increment/edit the `chapter_label` (including a `+1 Chapter` smart increment button that bumps `"Ch. 41"` -> `"Ch. 42"` automatically), and save optional quick context notes.
  3. On submit via HTMX:
     - Update `LibraryEntry.current_uri`, `chapter_label`, `source_domain`, and `last_read_at`.
     - Create an immutable `ReadingSnapshot` record logging the newly frozen URI and timestamp.
     - Return an instant visual confirmation badge (`"Snapshot Frozen at Ch. 42"`).
  4. Add a collapsible **"Snapshot History Drawer"** in the reader HUD so users can inspect or roll back to any previously frozen URI if a site restructures its links.
* **Commit Message:**
  ```text
  feat(reader): engineer State-Capture Snapshot tool with smart chapter increment and URI history
  ```
* **PR Documentation (`PR-5.2`):**
  * **Title:** `[FEAT] State-Capture ("Freeze Snapshot") Bookmarking & URI Rollback Drawer`
  * **Summary:** Implements the core manual state-persistence mechanism, logging every frozen chapter URI into `ReadingSnapshot` history and providing 1-click chapter increments.
  * **Verification:** Test snapshot creation, `source_domain` re-evaluation on URL change, smart chapter increment regex, and rollback to an older snapshot.

---

### PHASE 6: UX VALIDATION TELEMETRY & FINAL QUALITY ASSURANCE

#### Task 6.1: Usability Study Telemetry & "High Utility" Feedback Widget
* **Branch:** `feat/6.1-ux-validation-telemetry`
* **Action Items:**
  1. To directly support Objective 5 (*"Achieve a 60% or higher High Utility rating through a usability study with 10–15 active readers, focusing on time saved during session-start workflows"*), create a lightweight `UsabilityMetric` model in `library/models.py`.
  2. Track `session_start_to_resume_ms` (elapsed time from dashboard load to clicking **"Deep-Link Resume"**) and provide a built-in **"Usability Study Feedback Modal"** where test participants (10–15 readers) can submit their Utility Rating (`High Utility`, `Moderate Utility`, `Low Utility`) and qualitative feedback.
  3. Build a clean `/ux-metrics/` summary dashboard displaying average session-start time saved and the live percentage of "High Utility" ratings.
* **Commit Message:**
  ```text
  feat(telemetry): add session-start latency tracker and High Utility usability study dashboard
  ```
* **PR Documentation (`PR-6.1`):**
  * **Title:** `[FEAT] UX Validation & Session-Start Latency Telemetry`
  * **Summary:** Quantifies session-start workflow efficiency and tracks the 60%+ "High Utility" threshold for the 10–15 reader usability study.
  * **Verification:** Simulate usability study submissions and verify percentage calculation accuracy.

#### Task 6.2: End-to-End Integration Testing & Production Polish
* **Branch:** `chore/6.2-e2e-tests-and-docs`
* **Action Items:**
  1. Write comprehensive integration tests covering the full user lifecycle: Signup -> Create Folder/Tag -> Add Story with Custom Cover -> Omni-Search -> Deep-Link Resume -> Freeze Snapshot -> Export JSON Backup.
  2. Audit all templates against `modern-web-guidance` for keyboard navigation, focus states, and responsive mobile/desktop ergonomics.
  3. Generate `README.md` with setup instructions, architecture overview, and legal compliance statement (Non-Intrusive Pointer Architecture).
* **Commit Message:**
  ```text
  chore(qa): complete integration test suite, accessibility audit, and project documentation
  ```
* **PR Documentation (`PR-6.2`):**
  * **Title:** `[CHORE] End-to-End Test Suite & Final Release Readiness`
  * **Summary:** Finalizes automated tests across all apps (`accounts`, `library`, `reader`) and documents the full Git micro-chunk history.
  * **Verification:** `python manage.py test` passes 100% of test cases with zero warnings.

---

## 5. STANDARD PULL REQUEST (PR) TEMPLATE FOR ARGON AGENT

For every micro-task above, generate and log your PR documentation using this exact template before merging to `main`:

```markdown
## Pull Request: [TASK-ID] <Feature/Task Title>
**Source Branch:** `<branch_name>` -> **Target Branch:** `main`

### 1. Objective & Scope Alignment
- **OmniShelf Objective Addressed:** <e.g., Reading State Persistence / Contextual Resumption / Flexible Taxonomy>
- **Micro-Task Summary:** <Brief description of changes made in this isolated chunk>

### 2. Technical Changes
- **Models/Migrations:** <List any schema updates>
- **Views/URLs/HTMX Endpoints:** <List backend routes added/modified>
- **Templates/UI (`modern-web-guidance`):** <List frontend components updated>

### 3. Guardrail & Limitation Checklist
- [x] Zero story text/image scraping or copyright caching introduced.
- [x] Strict `request.user` tenancy isolation enforced on all queries.
- [x] All unit tests pass (`python manage.py test`).
```

---

## 6. IMMEDIATE EXECUTION COMMAND

**Argon Agent:** Begin execution immediately with **Phase 0, Task 0.1 (`chore/0.1-init-and-web-guidance`)**. Run `npx modern-web-guidance@latest install` first, verify the installation, scaffold the Django workspace, commit your changes, output the PR documentation for `PR-0.1`, merge to `main`, and proceed autonomously through Task 6.2.