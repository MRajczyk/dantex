from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Dantex:
    def __init__(self, email: str, password: str, driver):
        self.email = email
        self.password = password
        self.driver = driver

    def login_to_portal(self):
        elem = self.driver.find_element(By.ID, "id-username")
        elem.click()
        elem.clear()
        elem.send_keys(self.email)
        elem = self.driver.find_element(By.ID, "id-password")
        elem.click()
        elem.clear()
        elem.send_keys(self.password)
        elem.send_keys(Keys.RETURN)
        # check if logged in correctly
        try:
            # Timeout of 5 seconds waiting for modal to show up
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "modal-title"))
            )

            error_message = self.driver.find_element(By.CSS_SELECTOR, "div.bootbox-body b")
            if "Brak podanego użytkownika lub niewłaściwe hasło" in error_message.text:
                print("Błąd: Złe hasło lub brak użytkownika.")
                return

        except TimeoutException:
            if self.driver.current_url != "https://dante.iis.p.lodz.pl/#/mysubjects":
                print("Something went wrong when trying to log in.")
                exit()

    def export_all(self):
        self.driver.get("https://dante.iis.p.lodz.pl/")

        if self.driver.current_url == "https://dante.iis.p.lodz.pl/#/auth/login":
            self.login_to_portal()

        input("Press enter to end...")
        self.driver.close()