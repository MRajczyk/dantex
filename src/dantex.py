from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time


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
            WebDriverWait(self.driver, 3).until(
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

    def enable_disabled_buttons_by_text(self, text):
        self.enable_disabled_button_by_text(text)

    def enable_disabled_button_by_text(self, text):
        try:
            topics_list_button = self.driver.find_element(By.XPATH,
                                                          f"//button[@disabled and normalize-space(text())='{text}']")
            self.driver.execute_script("arguments[0].removeAttribute('disabled');", topics_list_button)

            return topics_list_button
        except:
            return None

    def change_disabled_visited_button_text(self, text):
        try:
            topics_list_button = self.driver.find_element(By.XPATH,
                                          f"//button[@disabled and normalize-space(text())='{text}']")
            self.driver.execute_script("arguments[0].innerText = 'visited';", topics_list_button)
        except:
            return

    def change_enabled_visited_button_text(self, text):
        try:
            topics_list_button = self.driver.find_element(By.XPATH,
                                          f"//button[normalize-space(text())='{text}']")
            self.driver.execute_script("arguments[0].innerText = 'visited';", topics_list_button)
        except:
            return

    def traverse_topic_list(self):
        topics_visited = 0
        while True:
            try:
                # check if topic list is loaded
                try:
                    WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        f"//button[normalize-space(text())='Lista zadań']")))
                except TimeoutException:
                    print("Something went wrong with loading exercise list for topic: {get and insert topic name (when bored enough)}")
                    self.driver.back()
                    continue
                except Exception as e:
                    print(e)
                    exit()

                for i in range(0, topics_visited):
                    self.change_enabled_visited_button_text("Lista zadań")
                button = self.driver.find_element(By.XPATH,
                                                    f"//button[normalize-space(text())='Lista zadań']")
                button.click()

                # go through exercises and scrape exercise content

                # if "Raport główny" is actvice, go to report page and download submitted files as well as test files

                time.sleep(3)
                self.driver.back()
                topics_visited += 1
            except Exception as e:
                print("Traversed all topics, going to a next course")
                break

    def export_all(self):
        self.driver.get("https://dante.iis.p.lodz.pl/")

        if self.driver.current_url == "https://dante.iis.p.lodz.pl/#/auth/login":
            self.login_to_portal()

        # self.enable_disabled_buttons_by_text("Lista tematów")
        courses_visited = 0
        while True:
            try:
                # check if courses list is loaded
                try:
                    WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH,
                                                f"//button[@disabled and normalize-space(text())='Lista tematów']")))
                except TimeoutException:
                    print("Something went wrong when going back in the history stack")
                    exit()
                except Exception as e:
                    print(e)

                for i in range(0, courses_visited):
                    self.change_disabled_visited_button_text("Lista tematów")
                button = self.enable_disabled_button_by_text("Lista tematów")
                button.click()

                # go through topic list
                self.traverse_topic_list()

                time.sleep(3)
                self.driver.back()
                courses_visited += 1
            except Exception as e:
                print(e)
                break

        input("Press enter to end...")
        self.driver.close()