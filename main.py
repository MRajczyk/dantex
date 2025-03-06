from dantex import Dantex
from selenium import webdriver
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()
    email = os.getenv("DANTE_EMAIL")
    password = os.getenv("DANTE_PASSWORD")

    dantex = Dantex(email, password, webdriver.Chrome())
    dantex.export_all()

#build modulu lokalnie
#pip install -e .