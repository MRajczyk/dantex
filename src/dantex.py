from selenium import webdriver


class Dantex:
    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password
        self.driver = webdriver.Chrome()

    def login_to_portal(self):
        self.driver.get("https://dante.iis.p.lodz.pl/")