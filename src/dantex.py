from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import os
import re


TIMEOUT_CONSTANT_TIME_IN_SECONDS = 10


# UTILS, CAN BE MOVED TO ANOTHER SCRIPT FILE LATER #
def create_directory(directory_name):
    try:
        os.makedirs("Dante export/" + directory_name)
        print(f"Directory '{directory_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{directory_name}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{directory_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")


def sanitize_filename_part(filename):
    return re.sub(r'[\\*?"<>|]', "_", filename.replace("/", "⁄").replace(":", "-"))


def change_download_directory(driver, folder_path):
    folder_abs = os.path.abspath(folder_path)
    params = {"behavior": "allow", "downloadPath": folder_abs}
    driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
    print(f"Folder changed to: {folder_abs}")
    # pesky nondeterminism, sometimes fails - saves to a default Downloads folder
    # problem now may have something to do with proceeding before download is finished (not tested yet)
    # TODO: work out a permanent fix
    time.sleep(0.5)


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
            WebDriverWait(self.driver, TIMEOUT_CONSTANT_TIME_IN_SECONDS).until(
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

    def change_enabled_visited_a_tag_text(self, text):
        try:
            topics_list_button = self.driver.find_element(By.XPATH,
                                          f"//a[normalize-space(text())='{text}']")
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

    def get_texts_from_breadcrumbs(self, expected_breadcrumbs_arr_length):
        try:
            WebDriverWait(self.driver, TIMEOUT_CONSTANT_TIME_IN_SECONDS).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "ol.breadcrumb li a")) >= expected_breadcrumbs_arr_length
            )
        except TimeoutException:
            print("Timed out when trying to get breadcrumbs.")
            return

        breadcrumb_items = self.driver.find_elements(By.CSS_SELECTOR, "ol.breadcrumb li a")
        breadcrumb_texts = [item.text for item in breadcrumb_items]

        return breadcrumb_texts

    def traverse_exercises(self, topic_number):
        # if "Raport główny" is actvice, go to report page and download submitted files as well as test files
        EXERCISE_BUTTON_TEXT = "Wykonaj"
        exercises_visited = 0
        while True:
            try:
                # check if topic list is loaded
                try:
                    WebDriverWait(self.driver, TIMEOUT_CONSTANT_TIME_IN_SECONDS).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        f"//a[normalize-space(text())='{EXERCISE_BUTTON_TEXT}']")))
                except TimeoutException:
                    print(
                        "Something went wrong when entering exercise {get and insert topic name (when bored enough)}")
                    return
                except Exception as e:
                    print(e)
                    exit()
                for i in range(0, exercises_visited):
                    self.change_enabled_visited_a_tag_text(EXERCISE_BUTTON_TEXT)
                button = self.driver.find_element(By.XPATH,
                                                  f"//a[normalize-space(text())='{EXERCISE_BUTTON_TEXT}']")
                button.click()
                # go through exercises and scrape exercise content
                self.save_exercise(topic_number, exercises_visited + 1)

                # time.sleep(3)
                self.driver.back()
                exercises_visited += 1
            except NoSuchElementException:
                print("Traversed all exercises, going to a next course")
                break
            except Exception as e:
                print(e)
                break
        return

    def get_report_files_if_present(self, exercise_name, exercise_folder_path):
        try:
            button = self.driver.find_element(By.XPATH,
                                              f"//a[normalize-space(text())='Raport główny']")
            previous_window = self.driver.window_handles[0]
            if "disabled" not in button.get_attribute("class"):
                button.click()
                # TODO: REMOVE NONDETERMINISM
                time.sleep(2)
                self.driver.switch_to.window(self.driver.window_handles[1])
                try:
                    sources_download_tag = self.driver.find_element(By.XPATH,
                                                      f"//a[normalize-space(text())='source.zip']")
                    change_download_directory(self.driver, exercise_folder_path)
                    sources_download_tag.click()
                except TimeoutException:
                    print("Błąd przy próbie pobrania przesłanego kodu źródłowego")
                finally:
                    # closing the tab regardless of saving results
                    # this is sketchy and dubious, but works, so stays for now :)
                    self.driver.close()
                    self.driver.switch_to.window(previous_window)
            else:
                print(f"Brak przesłanej odpowiedzi do zadania {exercise_name}")
        except TimeoutException:
            print("Błąd przy próbie pobrania raportu")
        except Exception as e:
            print(e)

    def save_exercise(self, topic_number, exercise_number):
        breadcrumb_texts = self.get_texts_from_breadcrumbs(5)
        # debug
        # print(breadcrumb_texts)
        # print("Dante export/" + sanitize_filename_part(breadcrumb_texts[1]) + "/" + sanitize_filename_part(breadcrumb_texts[2]) + "/" + sanitize_filename_part(breadcrumb_texts[3]) + ".html")
        create_directory(sanitize_filename_part(breadcrumb_texts[1]) + "/" + str(topic_number) + ". " + sanitize_filename_part(breadcrumb_texts[2])
                         + "/" + str(exercise_number) + ". " + sanitize_filename_part(breadcrumb_texts[3]))
        with open("Dante export/" + sanitize_filename_part(breadcrumb_texts[1]) + "/" + str(topic_number) + ". " + sanitize_filename_part(breadcrumb_texts[2])
                  + "/" + str(exercise_number) + ". " + sanitize_filename_part(breadcrumb_texts[3]) + "/"
                  + sanitize_filename_part(breadcrumb_texts[3]) + ".html", "w", encoding="utf-8") as f:
            f.write("<html>")
            exercise_contents = self.driver.find_element(By.ID, "taskwindow")
            contents = exercise_contents.get_attribute("outerHTML")
            f.write(contents)
            f.write("</html>")
            self.get_report_files_if_present(sanitize_filename_part(breadcrumb_texts[3]), "Dante export/" + sanitize_filename_part(breadcrumb_texts[1]) + "/" + str(topic_number) + ". " + sanitize_filename_part(breadcrumb_texts[2])
                         + "/" + str(exercise_number) + ". " + sanitize_filename_part(breadcrumb_texts[3]))

    def traverse_topic_list(self):
        TOPIC_BUTTON_TEXT = "Lista zadań"
        topics_visited = 12
        while True:
            try:
                # check if topic list is loaded
                try:
                    WebDriverWait(self.driver, TIMEOUT_CONSTANT_TIME_IN_SECONDS).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        f"//button[normalize-space(text())='{TOPIC_BUTTON_TEXT}']")))
                except TimeoutException:
                    print("Something went wrong with loading exercise list for topic: {get and insert topic name (when bored enough)}")
                    return
                except Exception as e:
                    print(e)
                    exit()

                for i in range(0, topics_visited):
                    self.change_enabled_visited_button_text(TOPIC_BUTTON_TEXT)
                button = self.driver.find_element(By.XPATH,
                                                    f"//button[normalize-space(text())='{TOPIC_BUTTON_TEXT}']")
                button.click()

                # go through exercises and scrape exercise content
                breadcrumb_texts = self.get_texts_from_breadcrumbs(4)
                create_directory(sanitize_filename_part(breadcrumb_texts[1]) + "/" + str(topics_visited + 1) + ". " + sanitize_filename_part(breadcrumb_texts[2]))
                self.traverse_exercises(topics_visited + 1)

                # time.sleep(3)
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
        TOPICS_LIST_BUTTON_TEXT = "Lista tematów"
        courses_visited = 3

        # go through courses
        while True:
            try:
                # check if courses list is loaded
                try:
                    WebDriverWait(self.driver, TIMEOUT_CONSTANT_TIME_IN_SECONDS).until(
                        EC.presence_of_element_located((By.XPATH,
                                                f"//button[@disabled and normalize-space(text())='{TOPICS_LIST_BUTTON_TEXT}']")))
                except TimeoutException:
                    print("Something went wrong when going back in the history stack")
                    exit()
                except Exception as e:
                    print(e)

                for i in range(0, courses_visited):
                    self.change_disabled_visited_button_text(TOPICS_LIST_BUTTON_TEXT)
                button = self.enable_disabled_button_by_text(TOPICS_LIST_BUTTON_TEXT)
                button.click()

                # go through topic list
                breadcrumb_texts = self.get_texts_from_breadcrumbs(3)
                create_directory(sanitize_filename_part(breadcrumb_texts[1]))
                self.traverse_topic_list()

                # time.sleep(3)
                self.driver.back()
                courses_visited += 1
            except Exception as e:
                print(e)
                break

        input("Press enter to end...")
        self.driver.close()
