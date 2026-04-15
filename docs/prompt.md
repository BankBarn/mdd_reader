# AI development prompt — mdd_reader

Use this file as **system or project context** when asking an AI assistant to modify or extend the **mdd_reader** codebase. Paste or attach it at the start of a session, or store it as a Cursor rule for this repository.

---

## Project identity

**mdd_reader** is a small Python toolkit for extracting information from the **My Dairy Dashboard** ecosystem:

- **Live automation** (`mdd_adminPanelScraper.py`): Selenium + Chrome logs into **`https://admin.mydairydashboard.com`**, walks **enterprise “other company”** pages to read **farm tables**, persists rows to **SQLite** (`enterprise.db`), then **impersonates** users and saves each farm’s **full page HTML** as a **pickle** under per-enterprise directories.
- **Offline parsing** (`data-reader.py`): Uses **BeautifulSoup** to extract **indicator card** fields from dashboard HTML: `.card-title`, `.mdd-indicator-container`, `.mdd-highcharts-footer`, scoped to `.card-container` or `mdd-indicator-card`.
- **Data access** (`sqlAPI.py`): CRUD-style helpers for `enterprise.db` — enterprises, farms, impersonation URLs, `clearFarms`, etc.

Supporting scripts: `excel-file-maker.py` prints joined enterprise/farm rows from the DB.

---

## Constraints for AI-generated changes

1. **Never add or preserve real passwords, API keys, or PII** in source code or docs. Use placeholders and environment variables.
2. **Prefer minimal diffs** that match existing style (imports, naming, no unnecessary abstractions).
3. **SQL**: Use parameterized queries (`?` placeholders) when touching `sqlAPI.py`; do not add more string-formatted SQL.
4. **Selenium**: Prefer explicit waits (`WebDriverWait`) over long fixed `sleep` where you touch that code; keep behavior equivalent unless asked to refactor broadly.
5. **Paths**: Do not assume Windows `C:\` paths; use configurable base directory via env var or function argument when adding new code.
6. **Dependencies**: If you add imports, update **`requirements.txt`** or **`install.txt`** consistently (the project currently lists packages in `install.txt`).

---

## Key files and responsibilities

| File | Responsibility |
|------|------------------|
| `mdd_adminPanelScraper.py` | Browser session, login flow, `companyCrawler`, `impersonateUser`, pickle writes. |
| `sqlAPI.py` | SQLite: `addFarm`, `clearFarms`, `getEnterpriseAccounts`, `getFarmsForDropdowns`, `getEnterpriseImpersonationAccountInfo`, `getFarmsAndEnterprise`. |
| `data-reader.py` | `extract_card_bits(html) -> list[dict]` with keys `title`, `data`, `footer`. |
| `excel-file-maker.py` | Iterates `getFarmsAndEnterprise()` for output. |

---

## Domain vocabulary

- **Enterprise / company**: A customer org in the admin portal; has a detail URL and a list of farms.
- **Farm account**: Row in the admin table + selectable entry in the impersonated dashboard dropdown.
- **Indicator card**: Dashboard widget; parsed fields map to marketing/ops KPIs and chart footers (e.g. “4-day avg on …”).

---

## Known technical debt (do not “fix” unless requested)

- Absolute XPath selectors and pagination via link text.
- `install.txt` missing `beautifulsoup4`.
- `data-reader.py` reads a local HTML filename that may not exist in-repo.
- Legacy string formatting in some SQL in `sqlAPI.py`.

When fixing debt, do so in **focused PR-sized steps** and update **`docs/README.md`** if behavior or setup changes.

---

## Typical extension tasks

- **Add JSON export** next to pickle dumps for downstream ETL.
- **Harden parsers** for additional card types or empty states.
- **Add CLI arguments** for dry-run, single-enterprise, or single-farm runs.
- **Add tests** for `extract_card_bits` using committed **sanitized** HTML fixtures (no real farm names if sensitive).

---

## Documentation map

- **`docs/README.md`** — setup, run commands, security notes.
- **`docs/PROJECT_OVERVIEW.md`** — product context, data flow, risks, roadmap.
- **`docs/prompt.md`** — this file.

When introducing new modules or workflows, update the relevant doc(s) in **`docs/`** in the same change.
