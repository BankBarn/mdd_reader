from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import sqlAPI

# --- Configuration ---
LOGIN_URL = "https://admin.mydairydashboard.com/#/"
EMAIL = "Brandon.mortas@ever.ag"
PASSWORD = "QGFj4pv2ZJqEy!Z"

# --- Start browser ---
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

#companies
'''pds = "https://admin.mydairydashboard.com/#/other-company-mdd/8152201"
gps = "https://admin.mydairydashboard.com/#/other-company-mdd/13789852"
elanco = "https://admin.mydairydashboard.com/#/other-company-mdd/33425262"
vitaplus ="https://admin.mydairydashboard.com/#/other-company-mdd/10641663"
cargill ="https://admin.mydairydashboard.com/#/other-company-mdd/401013428351"'''

def companyCrawler(url,id):
    wait = WebDriverWait(driver, 10)
    driver.get(url)
    data_rows = []
    time.sleep(2)
    while True:
        #Step 1: Wait for the table to be present
        table = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/jhi-main/div[2]/div/jhi-other-company-mdd-detail/div/div[2]")))
    # Step 2: Grab table rows (excluding header)
        rows = table.find_elements(By.XPATH, "/html/body/jhi-main/div[2]/div/jhi-other-company-mdd-detail/div/div[2]/table/tbody/tr")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [cell.text.strip() for cell in cells]
            #data_rows.append(row_data)
            sqlAPI.addFarm(id, row_data[0], row_data[1] )

    # Step 3: Try to go to next page
        try:
            next_btn = driver.find_element(By.LINK_TEXT, '»')

        # If next button is disabled or not clickable, break
            if "disabled" in next_btn.get_attribute("class").lower():
                break
            next_btn.click()
            time.sleep(2)  # small wait for table to update
        except:
            #print("No more pages or next button not found.")
            try:
                first_btn = driver.find_element(By.LINK_TEXT, '1')
                first_btn.click()
            except:
                print("small account")
                break
            time.sleep(3)
            break
    return data_rows

def impersonateUser():
    
    wait = WebDriverWait(driver, 10)
    driver.get("https://admin.mydairydashboard.com/#/user-management/auth0%7C642dc279d96731e35ad5e6a3")
    time.sleep(2)
        #Step 1: Wait for the table to be present
    impersonateBtn = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/jhi-main/div[2]/div/jhi-user-mgmt-detail/div/button[1]/span[2]")))
    impersonateBtn.click()
    time.sleep(2)
    print("here")
    #Switch to new tab opened
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(5)
    driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
    time.sleep(5)
    print("looking for Carlson")
    dropdownMenu = driver.find_element(By.ID, "mat-input-0").click()
    time.sleep(1)
    element = driver.find_element(By.XPATH, "//*[text()='CARLSON DAIRY LLP']").click()
    dropdownMenu = driver.find_element(By.ID, "mat-input-0").click()
    time.sleep(5)
    element = driver.find_element(By.XPATH, "//*[text()='SUNSET FARMS INC']").click()
    time.sleep(5)
    dropdownMenu = driver.find_element(By.ID, "mat-input-0").click()
    time.sleep(5)
    element = driver.find_element(By.XPATH, "//*[text()='Udder Dairy 2']").click()
    time.sleep(5)
    time.sleep(10)
    # Step 2: Grab table rows (excluding header)


def main():
    try:
        # Step 1: Open login page
        driver.get(LOGIN_URL)
        wait = WebDriverWait(driver, 10)
        next_btn = driver.find_element(By.XPATH, "/html/body/jhi-main/div[2]/div/jhi-home/div/div[2]/div/div/div/div/span/a")
        next_btn.click()

        # Step 2: Wait for email field and input email
        time.sleep(2)
        email_field = driver.find_element(By.XPATH, '//*[@id="username"]')
        email_field.send_keys(EMAIL)

        # Step 3: Click continue / next button
        next_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        next_btn.click()
        time.sleep(1)
        # Step 4: Wait for password field
        password_field = driver.find_element(By.XPATH, '//*[@id="password"]')
        password_field.send_keys(PASSWORD)

        # Step 5: Submit login
        login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_btn.click()

        # Step 6: Wait for successful login and redirect
        time.sleep(2)  # Adjust based on actual page load speed
        impersonateUser()
        ''' Off while testing impersonation
        sqlAPI.clearFarms()
        for i in sqlAPI.getEnterpriseAccounts():
            url = str(i[2])
            id = str(i[0])
            companyCrawler(url, id)'''
        '''companyCrawler(pds)
        companyCrawler(gps)
        companyCrawler(elanco)
        companyCrawler(vitaplus)
        companyCrawler(cargill)'''
        

    except Exception as e:
        print("An error occurred:", e)

    finally:
        driver.quit()


main()