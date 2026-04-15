# mdd_reader — documentation

This document describes the **active** pieces of this repository:

| Artifact | Role |
|----------|------|
| [`install.txt`](../install.txt) | Python packages to run the collector (`pip install -r install.txt`). |
| [`mdd_collector.py`](../mdd_collector.py) | Selenium + Chrome: logs into **app.mydairydashboard.com**, opens each processor dashboard from the DB, selects each farm, and downloads CSV via the column header menu (“Download CSV”). |
| [`sqlAPI.py`](../sqlAPI.py) | Reads **`mdd.db`**: lists processors (dashboards) and farm names per processor. |
| [`mdd.db`](../mdd.db) | SQLite database: `dashboards` and `farms` (see below). |

---

## Prerequisites

- **Python 3.x**
- **Google Chrome** (ChromeDriver is resolved via `webdriver-manager`)

---

## Database (`mdd.db`)

Expected tables (see `sqlite3 mdd.db '.schema'` if you need the live schema):

- **`dashboards`** — at least `id`, `url` (and `processor_name` in the current schema). Each row is one “processor” dashboard the script visits (`https://app.mydairydashboard.com/dashboards/<url>`).
- **`farms`** — `farm_name`, `processor_id` (links farms to `dashboards.id`).

Populate or migrate this file yourself; the repo does not ship a seed script.

---

## Setup

1. Create a virtual environment and install dependencies:

   ```bash
   pip install -r install.txt
   ```

2. **Credentials**: set **`MDD_APP_EMAIL`** and **`MDD_APP_PASSWORD`** in the environment. Do not rely on defaults in source for anything shared or public.

3. Place **`mdd.db`** in the project root (or change the path in `sqlAPI.py`).

4. Optional directories and tuning (see [Environment variables](#environment-variables)).

---

## Run

```bash
python mdd_collector.py
```

Flow: one browser session → login → for each row in `dashboards`, load that dashboard URL → for each farm name for that processor, select the farm, open the weight column menu, click the menu row whose text matches **`MDD_DOWNLOAD_MENU_TEXT`** (default `Download CSV`) → wait for the file under the download directory → repeat.

---

## Environment variables

| Variable | Purpose |
|----------|---------|
| `MDD_APP_EMAIL` | Login email for app.mydairydashboard.com |
| `MDD_APP_PASSWORD` | Login password |
| `MDD_DEBUG` | `1` / `true` / `yes` — extra step logging |
| `MDD_DOWNLOAD_DIR` | Chrome download folder (default: `./mdd_downloads`) |
| `MDD_DOWNLOAD_WAIT_SEC` | Max seconds to wait for a finished download (default `120`; `<=0` skips wait) |
| `MDD_DOWNLOAD_GRACE_SEC` | Extra sleep after a file appears (default `2`) |
| `MDD_DOWNLOAD_MENU_TEXT` | Substring to find on the menu item (default `Download CSV`) |
| `MDD_MENU_PANEL_ID` | If set, scope the menu to that overlay panel id; if empty, the script finds the **visible** item in any open Material menu (recommended when panel ids change each open) |
| `MDD_SAVE_FAILURE_ARTIFACTS` | With debug-like values, save menu failure screenshot/HTML (see `mdd_collector.py`) |
| `MDD_FAILURE_PREFIX` | Prefix for failure artifact filenames |

---

## Security

- Treat app credentials as secrets; use environment variables, not committed defaults, for shared copies of the repo.
- `sqlAPI.py` builds one query with `.format(processor_id)` for farm lookup; prefer parameterized queries if you extend it.

---

## Repository map (in scope)

```
mdd_reader/
├── install.txt
├── mdd_collector.py
├── sqlAPI.py
├── mdd.db
└── docs/
    ├── README.md           # this file
    ├── PROJECT_OVERVIEW.md
    └── prompt.md
```
