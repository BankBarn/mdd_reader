import os
import sys
import time
import traceback
import sqlAPI
import stage_to_databricks

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Override with MDD_APP_EMAIL / MDD_APP_PASSWORD in the environment when possible.
MDD_APP_EMAIL = os.environ.get("MDD_APP_EMAIL", "spadedata@spade.ag")
MDD_APP_PASSWORD = os.environ.get("MDD_APP_PASSWORD", "Sp@de2025!==")

STRICT_MENU_ITEM_CSS = "button.mat-mdc-menu-item, a.mat-mdc-menu-item"


def _mat_menu_item_xpath_by_visible_text(panel_id: str, label: str) -> str:
    """XPath for a Material menu row under #panel_id whose text contains `label` (e.g. Download CSV)."""
    if '"' in label:
        raise ValueError(
            "MDD_DOWNLOAD_MENU_TEXT must not contain double quotes (XPath string limitation)."
        )
    return (
        f"//div[@id='{panel_id}']//*[self::button or self::a]"
        f"[contains(@class,'mat-mdc-menu-item')]"
        f'[contains(normalize-space(.), "{label}")]'
    )


def _mat_menu_item_xpath_any_open_panel(label: str) -> str:
    """XPath for menu rows under any .mat-mdc-menu-panel (overlay panel id changes each open)."""
    if '"' in label:
        raise ValueError(
            "MDD_DOWNLOAD_MENU_TEXT must not contain double quotes (XPath string limitation)."
        )
    return (
        "//div[contains(@class,'mat-mdc-menu-panel')]"
        "//*[self::button or self::a][contains(@class,'mat-mdc-menu-item')]"
        f'[contains(normalize-space(.), "{label}")]'
    )


def _wait_visible_mat_menu_item(driver, wait: WebDriverWait, label: str, panel_id: str | None):
    """
    Return a displayed, enabled menu item. Angular gives each overlay a new id (mat-menu-panel-3,
    mat-menu-panel-4, ...), so prefer panel_id=None to scan any open panel and pick the visible row.
    """
    if '"' in label:
        raise ValueError(
            "MDD_DOWNLOAD_MENU_TEXT must not contain double quotes (XPath string limitation)."
        )

    def _visible_row(drv):
        xpath = (
            _mat_menu_item_xpath_by_visible_text(panel_id, label)
            if panel_id
            else _mat_menu_item_xpath_any_open_panel(label)
        )
        for el in drv.find_elements(By.XPATH, xpath):
            try:
                if el.is_displayed() and el.is_enabled():
                    return el
            except StaleElementReferenceException:
                continue
        return False

    return wait.until(_visible_row)


def _debug_enabled() -> bool:
    return os.environ.get("MDD_DEBUG", "").strip().lower() in ("1", "true", "yes")


def _debug_step(step: int, title: str, detail: str = "") -> None:
    if not _debug_enabled():
        return
    line = f"[MDD debug step {step}] {title}"
    if detail:
        line += f" — {detail}"
    print(line, flush=True)


def _safe_outer_html(el, limit: int = 400) -> str:
    try:
        raw = el.get_attribute("outerHTML") or ""
    except StaleElementReferenceException:
        return "<stale element>"
    if len(raw) > limit:
        return raw[:limit] + "…(truncated)"
    return raw


def _safe_elem_summary(el, index: int) -> list[str]:
    lines: list[str] = []
    try:
        tag = el.tag_name
        cls = el.get_attribute("class") or ""
        text = (el.text or "").strip().replace("\n", " ")
        role = el.get_attribute("role") or ""
        mid = el.get_attribute("id") or ""
        lines.append(
            f"    [{index}] <{tag}> id={mid!r} role={role!r}"
        )
        lines.append(f"         class: {cls!r}")
        lines.append(f"         text: {text!r}")
        lines.append(f"         outerHTML: {_safe_outer_html(el, 350)}")
    except StaleElementReferenceException:
        lines.append(f"    [{index}] <stale element>")
    return lines


def _menu_troubleshooting_report(driver, menu) -> str:
    """Human-readable diagnostics when strict menu-item count is wrong."""
    lines: list[str] = []
    lines.append("")
    lines.append("========== MDD troubleshooting: mat menu panel ==========")
    lines.append(
        "Failure: need at least 2 clickable rows using strict Material selectors."
    )
    lines.append(f"Strict selector: {STRICT_MENU_ITEM_CSS!r}")
    lines.append("")

    try:
        items_strict = menu.find_elements(By.CSS_SELECTOR, STRICT_MENU_ITEM_CSS)
    except StaleElementReferenceException:
        items_strict = []
        lines.append("Strict query: menu panel became stale; re-locate panel and retry.")

    lines.append(f"Strict match count: {len(items_strict)}")
    lines.append("Strict matches (what the script uses for item[1]):")
    for i, el in enumerate(items_strict):
        lines.extend(_safe_elem_summary(el, i))
    lines.append("")

    broader = [
        ('Any [role="menuitem"]', '[role="menuitem"]'),
        ("Any .mat-mdc-menu-item (any tag)", ".mat-mdc-menu-item"),
        ("Any button in panel", "button"),
        ("Any a in panel", "a"),
        ("mat-option (if menu uses select pattern)", "mat-option"),
    ]
    lines.append("Broader scans inside the same .mat-mdc-menu-panel (for comparison):")
    for label, css in broader:
        try:
            found = menu.find_elements(By.CSS_SELECTOR, css)
        except StaleElementReferenceException:
            found = []
        lines.append(f"  {label}: {len(found)} node(s)")
        for j, el in enumerate(found[:8]):
            lines.extend(_safe_elem_summary(el, j))
        if len(found) > 8:
            lines.append(f"    … {len(found) - 8} more not shown")
    lines.append("")

    try:
        outer = menu.get_attribute("outerHTML") or ""
    except StaleElementReferenceException:
        outer = "<stale>"
    lines.append("Menu panel outerHTML (first 3500 chars):")
    lines.append(outer[:3500] + ("…(truncated)" if len(outer) > 3500 else ""))
    lines.append("")
    lines.append("What to do next:")
    lines.append(
        "  1. Confirm the column menu actually lists 2+ actions in the live app."
    )
    lines.append(
        "  2. If yes, items may use a different tag/class — copy outerHTML above"
    )
    lines.append(
        "     and update STRICT_MENU_ITEM_CSS or the click index in mdd_collectorv2.py."
    )
    lines.append(
        "  3. Re-run with MDD_DEBUG=1 to print each step before the failure."
    )
    lines.append("=========================================================")

    if _debug_enabled() or os.environ.get("MDD_SAVE_FAILURE_ARTIFACTS", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        base = os.path.abspath(
            os.environ.get("MDD_FAILURE_PREFIX", "mdd_menu_failure")
        )
        png = base + ".png"
        html_path = base + ".html"
        try:
            driver.save_screenshot(png)
            lines.append(f"Saved screenshot: {png}")
        except Exception as e:
            lines.append(f"Could not save screenshot: {e}")
        try:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(outer if outer != "<stale>" else "")
            lines.append(f"Saved panel HTML: {html_path}")
        except OSError as e:
            lines.append(f"Could not save HTML: {e}")

    return "\n".join(lines)


def _default_download_dir() -> str:
    return os.path.abspath(
        os.environ.get("MDD_DOWNLOAD_DIR", os.path.join(os.getcwd(), "mdd_downloads"))
    )


def _list_download_names(directory: str) -> set[str]:
    try:
        return {
            n
            for n in os.listdir(directory)
            if not n.startswith(".") and n != ".DS_Store"
        }
    except OSError:
        return set()


def _is_chrome_partial_download_filename(name: str) -> bool:
    """True while Chrome is still writing (e.g. *.crdownload, including macOS names)."""
    return name.lower().endswith(".crdownload")


def _dismiss_blocking_overlays(driver, max_attempts: int = 12) -> None:
    """Close Material/CDK overlays (menus, backdrops) so the next click hits the page."""
    body = driver.find_element(By.TAG_NAME, "body")
    for _ in range(max_attempts):
        backdrops = driver.find_elements(
            By.CSS_SELECTOR,
            "div.cdk-overlay-backdrop.cdk-overlay-backdrop-showing",
        )
        if not any(b.is_displayed() for b in backdrops):
            return
        body.send_keys(Keys.ESCAPE)
        time.sleep(0.25)


def _wait_for_chrome_download(
    download_dir: str,
    before: set[str],
    *,
    timeout_sec: float,
    grace_sec: float,
) -> list[str]:
    """Wait for a new file to appear and Chrome to finish (.crdownload gone)."""
    deadline = time.monotonic() + timeout_sec
    last_partial_log = 0.0
    while time.monotonic() < deadline:
        try:
            names = set(os.listdir(download_dir))
        except OSError:
            time.sleep(0.2)
            continue

        partial = [n for n in names if _is_chrome_partial_download_filename(n)]
        if partial:
            if _debug_enabled():
                now = time.monotonic()
                if now - last_partial_log > 2.0:
                    print(
                        f"[MDD debug] Download in progress: partial={partial!r}",
                        flush=True,
                    )
                    last_partial_log = now
            time.sleep(0.2)
            continue

        new_names = _list_download_names(download_dir) - before
        if not new_names:
            time.sleep(0.2)
            continue

        ready: list[str] = []
        for n in new_names:
            if _is_chrome_partial_download_filename(n):
                continue
            path = os.path.join(download_dir, n)
            try:
                if os.path.isfile(path) and os.path.getsize(path) > 0:
                    ready.append(n)
            except OSError:
                pass

        if ready:
            if grace_sec > 0:
                time.sleep(grace_sec)
            return sorted(ready)

        time.sleep(0.2)

    raise TimeoutError(
        f"No completed download in {download_dir!r} within {timeout_sec}s "
        f"(before files: {sorted(before)!r})."
    )


class mdd_reader:
    def setup_method(self, method):
        self.download_dir = _default_download_dir()
        os.makedirs(self.download_dir, exist_ok=True)

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=options,
        )
        self.vars = {}

    def teardown_method(self, method):
        if getattr(self, "driver", None):
            self.driver.quit()

    def mdd_login(self):
        # Navigate to login page
        _debug_step(1, "Load login page", "GET app.mydairydashboard.com/login")
        self.driver.get("https://app.mydairydashboard.com/login")

        # Accept cookie consent if present
        try:
            WebDriverWait(self.driver, 5).until(
                expected_conditions.visibility_of_element_located(
                    (By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
                )
            )
            self.driver.find_element(
                By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"
            ).click()
            _debug_step(2, "Cookie banner", "clicked Allow all")
        except Exception:
            _debug_step(2, "Cookie banner", "not shown or skipped")
            pass  # Cookie banner may not always appear

        # Wait for email field and enter email
        WebDriverWait(self.driver, 5).until(
            expected_conditions.visibility_of_element_located((By.ID, "mat-input-0"))
        )
        self.driver.find_element(By.ID, "mat-input-0").send_keys(MDD_APP_EMAIL)
        _debug_step(3, "Email field", "filled #mat-input-0")

        # Click the submit button to proceed to password page
        element = self.driver.find_element(By.NAME, "submit")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        self.driver.find_element(By.NAME, "submit").click()
        _debug_step(4, "Submit email", "clicked [name=submit]")

        # Wait for password field and enter password
        WebDriverWait(self.driver, 5).until(
            expected_conditions.visibility_of_element_located((By.ID, "password"))
        )
        self.driver.find_element(By.ID, "password").send_keys(MDD_APP_PASSWORD)
        self.driver.find_element(By.ID, "password").send_keys(Keys.ENTER)
        _debug_step(5, "Password", "submitted #password")

    def dashboard_load(self, processor):
        url = "https://app.mydairydashboard.com/dashboards/" + processor[1]
        self.driver.get(url)
        time.sleep(5)
        for farm in sqlAPI.get_farm_info_for_processor(processor[0]):
            print(farm[0])
            _dismiss_blocking_overlays(self.driver)
            dropdownMenu = self.driver.find_element(By.ID, "mat-input-0")
            dropdownMenu.click()
            time.sleep(1)
            #this resets the dropdown to look at the first account in the list incase it is at the bottom
            dropdownMenu.send_keys(Keys.CONTROL, "a")
            dropdownMenu.send_keys(Keys.DELETE)
            # Wait for dashboard to load and click column header
            self.driver.find_element(By.ID, "mat-input-0").click()
            try:
                element = self.driver.find_element(By.XPATH, "//*[text()='{}']".format(farm[0])).click()
                time.sleep(5)
                print("Not Found")
            except:
                print("Farm not found")
            WebDriverWait(self.driver, 10).until(
                expected_conditions.visibility_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        ".mat-mdc-header-row > .cdk-column-id_weight_pound:nth-child(3)",
                    )
                )
            )
            self.driver.find_element(
                By.CSS_SELECTOR,
                ".mat-mdc-header-row > .cdk-column-id_weight_pound:nth-child(3)",
            ).click()
            _debug_step(
                6,
                "Weight column header",
                "clicked .cdk-column-id_weight_pound (sort/header)",
            )

            # Scroll to top (matches legacy mdd_collector.py)
            self.driver.execute_script("window.scrollTo(0,0)")
            _debug_step(7, "Scroll", "window.scrollTo(0,0)")

            # Legacy Selenium IDE flow from mdd_collector.py — same selectors/XPath as before.
            wait = WebDriverWait(self.driver, 15)
            trigger_css = ".mat-mdc-menu-trigger:nth-child(1)"
            element = wait.until(
                expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, trigger_css)
                )
            )
            _debug_step(8, "Menu trigger", trigger_css)
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
            self.driver.find_element(By.CSS_SELECTOR, trigger_css).click()
            _debug_step(9, "Menu trigger", "clicked")
            time.sleep(1)
            # Empty/unset MDD_MENU_PANEL_ID: find the visible row (panel #id changes every open).
            panel_id_raw = os.environ.get("MDD_MENU_PANEL_ID", "").strip()
            panel_id = panel_id_raw or None
            menu_label = os.environ.get("MDD_DOWNLOAD_MENU_TEXT", "Download CSV")
            menu_item = _wait_visible_mat_menu_item(
                self.driver, wait, menu_label, panel_id
            )
            before_downloads = _list_download_names(self.download_dir)
            menu_item.click()
            loc = (
                f"panel_id={panel_id_raw!r} label={menu_label!r}"
                if panel_id
                else f"any open mat-mdc-menu-panel label={menu_label!r}"
            )
            _debug_step(10, "Menu item by label", loc)

            # Keep the browser session until Chrome finishes saving the file (avoids quit() mid-download).
            wait_sec = float(os.environ.get("MDD_DOWNLOAD_WAIT_SEC", "120"))
            grace = float(os.environ.get("MDD_DOWNLOAD_GRACE_SEC", "2"))
            if wait_sec > 0:
                _debug_step(
                    11,
                    "Waiting for download",
                    f"dir={self.download_dir!r} timeout={wait_sec}s",
                )
                try:
                    finished = _wait_for_chrome_download(
                        self.download_dir,
                        before_downloads,
                        timeout_sec=wait_sec,
                        grace_sec=grace,
                    )
                    self.driver.get(url)
                    time.sleep(5)
                except TimeoutError as e:
                    print(str(e), file=sys.stderr)
                    raise
                print(
                    f"Download finished ({len(finished)} file(s)): {finished}",
                    flush=True,
                )
                _dismiss_blocking_overlays(self.driver)
            else:
                _debug_step(
                    11,
                    "Download wait skipped",
                    "MDD_DOWNLOAD_WAIT_SEC<=0",
                )
                _dismiss_blocking_overlays(self.driver)


def main():
    reader = mdd_reader()
    reader.setup_method(None)
    try:
        reader.mdd_login()
        for processor in sqlAPI.list_of_processors():
            reader.dashboard_load(processor)
    finally:
        reader.teardown_method(None)


if __name__ == "__main__":
    try:
        main()
        stage_to_databricks.main()
    except Exception as exc:
        print(exc, file=sys.stderr)
        if _debug_enabled():
            traceback.print_exc()
        sys.exit(1)
