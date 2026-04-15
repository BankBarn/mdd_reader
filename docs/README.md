# mdd_reader — documentation

This folder contains the canonical documentation for the **mdd_reader** repository: tooling used to pull structured information from the **My Dairy Dashboard (MDD)** ecosystem, primarily via the **MyDairy admin portal** (`admin.mydairydashboard.com`).

For a product- and architecture-oriented summary, see [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md). For AI-assisted development context, see [prompt.md](./prompt.md).

---

## What this repository does

| Component | Role |
|-----------|------|
| `mdd_adminPanelScraper.py` | Selenium automation: admin login, per-enterprise “company” table crawl, farm rows written to SQLite, then user impersonation and per-farm dashboard HTML saved as pickle files. |
| `sqlAPI.py` | SQLite access layer for `enterprise.db` (enterprises, farms, impersonation URLs). |
| `data-reader.py` | Parses saved or sample HTML to extract **indicator card** content (title, body, footer) using BeautifulSoup. |
| `excel-file-maker.py` | Thin script that prints joined enterprise/farm rows from the database (intended for export or inspection). |
| `install.txt` | Python package list for a minimal environment (see [Setup](#setup)). |

---

## Prerequisites

- **Python 3.x**
- **Google Chrome** (for Selenium + ChromeDriver via `webdriver-manager`)
- A populated **`enterprise.db`** with tables and rows the code expects (`enterprise_customers`, `enterprise_user`, `farms`, etc.). The repository does not ship a schema migration or seed file; the database is assumed to exist locally.

---

## Setup

1. Create a virtual environment and install dependencies:

   ```bash
   pip install -r install.txt
   pip install beautifulsoup4
   ```

   `data-reader.py` requires **BeautifulSoup** (`bs4`); it is not listed in `install.txt` today.

2. **Credentials and paths**: `mdd_adminPanelScraper.py` is written for a specific machine layout and contains admin portal login settings. Before running anything, configure login and output paths via **environment variables** or a local config file that is **gitignored** — do not commit secrets. Rotate any credentials that were ever committed to version control.

3. Place or generate **`enterprise.db`** in the project root (or adjust connection paths in `sqlAPI.py`).

4. Optional: for `data-reader.py`, provide a sample HTML file (e.g. exported dashboard markup) as referenced in that script, or change the input path.

---

## Running the pieces

- **Admin scraper** (long-running; drives a real browser):

  ```bash
  python mdd_adminPanelScraper.py
  ```

  Expects Windows-style absolute paths in the current code for data directories; adjust for your OS or use configurable base paths.

- **HTML card extraction** (offline parsing):

  ```bash
  python data-reader.py
  ```

- **List farms and enterprises**:

  ```bash
  python excel-file-maker.py
  ```

---

## Data and outputs

- **SQLite (`enterprise.db`)**: Stores enterprise metadata, farm names, and MDD identifiers; the scraper refreshes the `farms` table during a run (`clearFarms` then repopulates from portal tables).
- **Pickle files**: Full-page HTML (`page_source`) per farm account, written under a configurable enterprise data directory for later parsing (e.g. with `data-reader.py` patterns).

---

## Security

- Treat admin portal credentials like production secrets: use environment variables or a secret manager, and remove hardcoded passwords from source before sharing or publishing the repo.
- The SQLite helpers use string formatting for SQL in places; prefer parameterized queries when extending this code to avoid injection issues.

---

## Repository map

```
mdd_reader/
├── data-reader.py          # HTML → structured card fields
├── mdd_adminPanelScraper.py
├── sqlAPI.py
├── excel-file-maker.py
├── install.txt
└── docs/
    ├── README.md           # this file
    ├── PROJECT_OVERVIEW.md
    └── prompt.md
```

---

## Contributing / next steps

See [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) for known gaps and suggested improvements. When adding features, update this README and [prompt.md](./prompt.md) so automation and future contributors stay aligned.
