from dantex import Dantex

if __name__ == "__main__":
    scraper = Dantex("login", "password")
    scraper.login_to_portal()

    while True:
        continue

#build modulu lokalnie
#pip install -e .