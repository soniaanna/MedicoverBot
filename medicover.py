from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from time import sleep
import datetime
import sys
#from medicover.sms import send_sms

class Medicover():
    def __init__(self):
        self.driver = webdriver.Chrome('chromedriver')
        self.driver.get("https://mol.medicover.pl")
        self.main_window = self.driver.current_window_handle
        self.card_no = ''
        self.password= ''

    def logged(self):
        self.driver.switch_to.window(self.main_window)
        return len(self.driver.find_elements_by_id("logoff")) == 1

    def login(self, card_no, password):
        if not self.logged():
            self.card_no = card_no
            self.password = password
            self.driver.get("https://mol.medicover.pl")
            self.driver.find_element_by_id('oidc-submit').click()
            login_window = list(set(self.driver.window_handles) - {self.main_window})[0]
            self.driver.switch_to.window(login_window)
            self.driver.find_element_by_id("username-email").send_keys(card_no)
            self.driver.find_element_by_id("password").send_keys(password)
            self.driver.find_element_by_css_selector("div.form-group button.btn.btn-block.btn-primary").click()

    def find_doc(self, region=202, special=42, doc_id=231862, start_hour=0, end_hour=0):
        if self.logged():
            if doc_id:
                doc_id='&doctorId=' + str(doc_id)
            self.driver.switch_to.window(self.main_window)
            search_since = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:02.156Z')
            self.driver.get(f"https://mol.medicover.pl/MyVisits?regionId={region}&bookingTypeId=2&specializationId={special}&languageId=-1{doc_id}&searchSince={search_since}&startTime={start_hour}&endTime={end_hour}")

            while True:
                sleep(5)
                try:
                    self.driver.find_element_by_xpath("//button[text()='Szukaj']").click()
                except ElementClickInterceptedException:
                    self.driver.find_element_by_id('btn-session-refresh').click()
                sleep(10)
                if "Wizyty do lekarza wybranej specjalizacji zostały już zarezerwowane przez innych pacjentów." not in self.driver.page_source:
                    self.driver.find_element_by_css_selector("div.freeSlot div div button.btn.btn-sm").click()
                    apo_time = self.driver.find_element_by_css_selector("div.visit-date").text
                    specialization = self.driver.find_element_by_id('FormModel_SpecializationName').get_attribute('value')
                    doc_name = self.driver.find_element_by_id('FormModel_DoctorName').get_attribute('value')
                    clinic = self.driver.find_element_by_id('FormModel_ClinicPublicName').get_attribute('value')
                    self.driver.find_element_by_id("bookAppointmentButton").click()
                    print(apo_time)
                    print(specialization)
                    print(doc_name)
                    print(clinic)
 #                   send_sms(f'{apo_time} {specialization} {doc_name} {clinic}')
                    break
        else:
            self.login(self.card_no, self.password)
            self.find_doc(region=region, special=special, doc_id=doc_id, start_hour=start_hour, end_hour=end_hour)

#from twilio.rest import Client

#def send_sms(text):
#    client = Client("", "")
#    client.messages.create(to="", from_="", body=text)


spec_id = {"x": 0}

doc_ids = {"x x": 0}

med_bot = Medicover()
med_bot.login('', '')
med_bot.find_doc(doc_id='', special=42)

# 1. Install selenium - pip install selenium
# 2. Download chromedriver for your browser (version is important) and put it in any directory from PATH
# 3. In med_bot.login provide your card no and password
# 4. Provide doctor id (if empty, all are selected) and specialization
# 5. IDs can be found while manually looking for appointment
