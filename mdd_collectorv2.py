import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class mdd_reader():

    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_newTest(self):
        # Navigate to login page
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
        except Exception:
            pass  # Cookie banner may not always appear

        # Wait for email field and enter email
        WebDriverWait(self.driver, 5).until(
            expected_conditions.visibility_of_element_located((By.ID, "mat-input-0"))
        )
        self.driver.find_element(By.ID, "mat-input-0").send_keys("spadedata@spade.ag")

        # Click the submit button to proceed to password page
        element = self.driver.find_element(By.NAME, "submit")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        self.driver.find_element(By.NAME, "submit").click()

        # Wait for password field and enter password
        WebDriverWait(self.driver, 5).until(
            expected_conditions.visibility_of_element_located((By.ID, "password"))
        )
        self.driver.find_element(By.ID, "password").send_keys("Sp@de2025!==")
        self.driver.find_element(By.ID, "password").send_keys(Keys.ENTER)

        # Wait for dashboard to load and click column header
        WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, ".mat-mdc-header-row > .cdk-column-id_weight_pound:nth-child(3)")
            )
        )
        self.driver.find_element(
            By.CSS_SELECTOR, ".mat-mdc-header-row > .cdk-column-id_weight_pound:nth-child(3)"
        ).click()

        # Scroll to top
        self.driver.execute_script("window.scrollTo(0,0)")

        # Open menu and click second option
        element = self.driver.find_element(By.CSS_SELECTOR, ".mat-mdc-menu-trigger:nth-child(1)")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        self.driver.find_element(By.CSS_SELECTOR, ".mat-mdc-menu-trigger:nth-child(1)").click()

        WebDriverWait(self.driver, 5).until(
            expected_conditions.visibility_of_element_located(
                (By.XPATH, "(//div[@id='mat-menu-panel-3']/div/button[2]/span)[1]")
            )
        )
        self.driver.find_element(
            By.XPATH, "(//div[@id='mat-menu-panel-3']/div/button[2]/span)[1]"
        ).click()

