import schedule
import time
import json
import yagmail
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginException(Exception):
    pass

class NoAdsFoundException(Exception):
    pass

class EmailSender:
    def __init__(self, email, password, receiver_list):
        self.yagmail = yagmail.SMTP(email, password)
        self.receiver_list = receiver_list
        self.subject = "Milanuncios Updater"

    def send_email(self, message):
        for receiver in self.receiver_list:
            self.yagmail.send(receiver, self.subject, message)

class MilanunciosScrapper:
    DAILY_DELAY_IN_SECONDS = 20
    MAXIMUM_DAILY_DELAY_IN_SECONDS = 3600
    DEFAULT_TIMEOUT_IN_SECONDS = 10
    SCROLL_WAIT = 0.4

    def __init__(self, email, password, chrome_options, email_sender):
        self.email = email
        self.password = password
        self.chrome_options = chrome_options
        self.email_sender = email_sender    
        self.current_daily_delay = 0    

    def do_update(self):
        print("[", datetime.now(), "] Execution. Current daily delay = ", self.current_daily_delay)
        time.sleep(self.current_daily_delay)
        self.number_of_updated_ads = 0
        self.number_of_already_updated_ads = 0

        try:
            self.driver = webdriver.Chrome("./chromedriver_linux64/chromedriver", options=self.chrome_options)        
            self.driver.get('https://www.milanuncios.com/mis-anuncios')
            self.accept_cookies_if_exist()
            self.login(self.email, self.password)
            self.close_popup_if_exist()
            self.update_ads()
            self.report_result()
        except Exception as e:
            self.email_sender.send_email("Error en la actualización: ", e)
        if(self.current_daily_delay > self.MAXIMUM_DAILY_DELAY_IN_SECONDS):
            self.current_daily_delay = 0
        else:
            self.current_daily_delay += self.DAILY_DELAY_IN_SECONDS

    def accept_cookies_if_exist(self):
        accept_cookies_button = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT_IN_SECONDS).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='TcfAccept']"))
        )
        if(accept_cookies_button is not None):
            accept_cookies_button.click()

    def login(self, email, password):
        self.driver.find_element_by_css_selector("nav button.ma-ButtonBasic:last-child").click()
        email_input = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT_IN_SECONDS).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        password_input = self.driver.find_element_by_id("password")

        email_input.click()
        email_input.send_keys(email)
        password_input.click()
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)

    def close_popup_if_exist(self):
        ok_button = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT_IN_SECONDS).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ma-ModalOnboardingReserved-contentFooterButton button"))
        )

        ok_button.click()
        
    def update_ads(self):
        WebDriverWait(self.driver, self.DEFAULT_TIMEOUT_IN_SECONDS).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "footer"))
        )

        time.sleep(5)
        self.load_all_ads()
        update_ad_button_list = self.driver.find_elements_by_css_selector("ul.ma-AdButtonBarMyAds li:nth-child(2)")

        if(not update_ad_button_list):
            raise NoAdsFoundException("No se encontraron anuncios en tu cuenta.")

        for button in update_ad_button_list:
            button.click()
            self.process_if_ad_already_updated()
    
    def load_all_ads(self):
        continue_scrolling = True
        scrolling = 0
        while continue_scrolling:
            scrolling += 400
            self.driver.execute_script("window.scrollTo(0, " + str(scrolling) + ")")
            time.sleep(self.SCROLL_WAIT)
            self.driver.execute_script("window.scrollTo(0, 0)")
            time.sleep(self.SCROLL_WAIT)
            second_scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            if scrolling >= second_scroll_height:
                continue_scrolling = False
            

    def process_if_ad_already_updated(self):
        try:
            button_close_modal = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".is-MoleculeModal-open div.ma-ModalRenewAd-iconClose"))
            )
            button_close_modal.click()
            self.number_of_already_updated_ads += 1
        except Exception:
            self.number_of_updated_ads += 1
    
    def report_result(self):
        print("[", datetime.now(), "] Execution ended. Updated ads: ", str(self.number_of_updated_ads) + " . Already updated ads: " + str(self.number_of_already_updated_ads))
        message = "Actualización completada. Se han actualizado " + str(self.number_of_updated_ads) + " anuncios. Otros " + str(self.number_of_already_updated_ads) + " ya estaban actualizados."
        self.email_sender.send_email(message)

def main():
    with open('config.json', 'r') as f:
        config = json.load(f)

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    email_sender = EmailSender(config['notifications']['from']['email'], config['notifications']['from']['password'], config['notifications']['to'])
    milanuncios_email = config['milanuncios']['email']
    milanuncios_password = config['milanuncios']['password']
    milanuncios_scrapper = MilanunciosScrapper(milanuncios_email, milanuncios_password, options, email_sender)

    milanuncios_scrapper.do_update()
    schedule.every().day.at(config['updateTime']).do(milanuncios_scrapper.do_update)

    while True:
        schedule.run_pending()
        time.sleep(60)
    
if __name__ == "__main__":
    main()
