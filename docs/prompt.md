# AI development prompt — mdd_reader

Use this file as **project context** when modifying automation for **My Dairy Dashboard** in this repository.

**In scope:** only **`install.txt`**, **`mdd_collector.py`**, **`sqlAPI.py`**, and **`mdd.db`**. Ignore legacy or archived scripts unless the user explicitly expands scope.

---

## What the project does

- **`mdd_collector.py`**: Selenium + Chrome — login to **app.mydairydashboard.com**, iterate processors and farms from the database, trigger **Download CSV** (or **`MDD_DOWNLOAD_MENU_TEXT`**) from the dashboard column menu, save files to a download directory.
- **`sqlAPI.py`**: SQLite reads against **`mdd.db`** — `list_of_processors()`, `get_farm_info_for_processor(id)`.
- **`mdd.db`**: Tables **`dashboards`** and **`farms`** (processor list + farm names per processor).
- **`install.txt`**: Lists **`selenium`** and **`webdriver-manager`** for `pip install -r install.txt`.

---

## Constraints for AI-generated changes

1. **Secrets**: Do not add or preserve real passwords in source. Prefer **`MDD_APP_EMAIL`** / **`MDD_APP_PASSWORD`** and document them in **`docs/README.md`** only as variable names.
2. **Minimal diffs**: Match existing style in **`mdd_collector.py`** and **`sqlAPI.py`**.
3. **SQL**: Prefer parameterized queries (`?`) in **`sqlAPI.py`** when changing queries.
4. **Selenium**: Prefer **`WebDriverWait`** and existing helpers (`_wait_visible_mat_menu_item`, `_dismiss_blocking_overlays`) over new long sleeps unless necessary.
5. **Dependencies**: New imports require updating **`install.txt`**.

---

## Documentation

- **`docs/README.md`** — setup, run, environment variables, **`mdd.db`** shape.
- **`docs/PROJECT_OVERVIEW.md`** — flow diagram, risks.
- **`docs/prompt.md`** — this file.

Update the relevant doc when behavior or setup changes.
