import time
import json
import yagmail
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginException:
    pass

class NoAdsFoundException:
    pass

class EmailSender:
    def __init__(self):
        super().__init__()

    def send_email(self, to, message):
        print("done")

class MilanunciosScrapper:
    def __init__(self, chrome_opts):
        self.driver = webdriver.Chrome("./chromedriver_linux64/chromedriver", chrome_options=chrome_opts)
        self.driver.get('https://www.milanuncios.com/mis-anuncios')

    def accept_cookies_if_exist(self):
        accept_cookies_button = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='TcfAccept']"))
        )
        if(accept_cookies_button is not None):
            accept_cookies_button.click()

    def login(self, email, password):
        self.driver.find_element_by_css_selector("nav button.ma-ButtonBasic:last-child").click()
        email_input = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        password_input = self.driver.find_element_by_id("password")

        email_input.click()
        email_input.send_keys(email)
        password_input.click()
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)

    def close_popup_if_exist(self):
        ok_button = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ma-ModalOnboardingReserved-contentFooterButton button"))
        )

        ok_button.click()
        
    def update_ads(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.ma-AdButtonBarMyAds li:nth-child(2)"))
        )
        
        update_ad_button_list = self.driver.find_elements_by_css_selector("ul.ma-AdButtonBarMyAds li:nth-child(2)")
        if(not update_ad_button_list):
            raise NoAdsFoundException("No se encontraron anuncios en tu cuenta.")

        for button in update_ad_button_list:
            button.click()
        

def main():
    with open('config.json', 'r') as f:
        config = json.load(f)

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    milanuncios_scrapper = MilanunciosScrapper(None)

    milanuncios_scrapper.accept_cookies_if_exist()
    milanuncios_scrapper.login(config['milanuncios']['email'], config['milanuncios']['password'])
    milanuncios_scrapper.close_popup_if_exist()
    milanuncios_scrapper.update_ads()
    time.sleep(10)
    
if __name__ == "__main__":
    main()
