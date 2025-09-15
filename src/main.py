import csv
import os
import time
from time import sleep

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from exceptions import DaftRentalBotLoginError
from generate_data import GenerateLink
from generate_data import generate_end_time

# --- XPATH/CSS SELECTORS AS VARIABLES ---
DAFT_URL = "http://www.daft.ie"
COOKIE_ACCEPT_XPATH = '//*[@id="didomi-notice-agree-button"]'  # Update as needed after inspecting site
SIGNIN_BUTTON_XPATH = '//*[@id="__next"]/div[2]/header/div/div[2]/div[3]/ul/li/a' # //*[@id="__next"]/div[2]/header/div/div[2]/div[3]/ul/li/a
EMAIL_FIELD_XPATH = '//*[@id="username"]'
PASSWORD_FIELD_XPATH = '//*[@id="password"]'
SUBMIT_LOGIN_XPATH = '//*[@id="login"]'
LOGIN_SUCCESS_XPATH = '//*[@id="__next"]/div[2]/header/div/div[2]/div[3]/ul/li/div/div[1]/div/button'  # Update as needed after inspecting site
LATEST_AD_XPATH = '//*[@id="__next"]/main/div[3]/div[1]/ul/li[1]/a/div/div[1]/div[2]'
ADDRESS_XPATH = '//*[@id="__next"]/main/div[3]/div[1]/div[1]/div[1]/div[1]/h1'
PRICE_XPATH = '//*[@id="__next"]/main/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/h2'
EMAIL_BUTTON_XPATH = '//*[@id="__next"]/main/div[3]/div[2]/div[1]/div[2]/button'
FIRSTNAME_FIELD_XPATH = '//*[@id=":r0:"]'
LASTNAME_FIELD_XPATH = '//*[@id=":r1:"]'
EMAILID_FIELD_XPATH = '//*[@id=":r2:"]'
CONTACT_FIELD_XPATH = '//*[@id=":r3:"]'
PEOPLE_INCREAMENT_BUTTON_XPATH = '//*[@id="__next"]/main/div[3]/div[1]/div[18]/div/div/div/div/form/div[3]/div[1]/div[1]/div/div/div/button[2]'
NO_PET_RADIO_XPATH = '//*[@id="__next"]/main/div[3]/div[1]/div[18]/div/div/div/div/form/div[3]/div[2]/div[2]/div/div/label[2]/input'
MESSAGE_FIELD_XPATH = '//*[@id=":r7:"]'
SEND_APPLICATION_XPATH = '//*[@id="__next"]/main/div[3]/div[1]/div[18]/div/div/div/div/form/div[5]/button'
CLOSE_MODAL_XPATH = '//*[@id="__next"]/main/div[3]/div[1]/div[18]/div/div/div/header/div/button'
ALREADY_APPLIED_XPATH = '//*[@id="__next"]/div[1]/div'
FEEDBACK_CLOSE_XPATH = '//*[@id="wootric-close"]'
# --- END SELECTORS ---

class SetUp:
    def __init__(self):
        load_dotenv(".env")
        self.SECRET_ID = os.environ.get("secretUser")
        self.SECRET_PASSWORD = os.environ.get("secretPassword")
        self.SECRET_FNAME = os.environ.get("secretFName")
        self.SECRET_LNAME = os.environ.get("secretLName")
        self.SECRET_CONTACT = os.environ.get("secretContact")
        self.SECRET_MESSAGE = os.environ.get("secretMessage")

        # Create new csv file to log submissions
        self.file = open("logger.csv", "a")
        self.writer = csv.writer(self.file)

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.set_page_load_timeout(30)

    def login(self):
        self.driver.get(DAFT_URL)

        self.driver.maximize_window()

        # Wait for and click the policy button
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, COOKIE_ACCEPT_XPATH))
        ).click()

        # Wait for and click the sign-in button
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, SIGNIN_BUTTON_XPATH))
        ).click()

        # Wait for and fill the email field
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, EMAIL_FIELD_XPATH))
        ).send_keys(self.SECRET_ID)

        # Wait for and fill the password field
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, PASSWORD_FIELD_XPATH))
        ).send_keys(self.SECRET_PASSWORD)


        # Pause for 1 second before clicking submit
        sleep(1)

        # Wait for and click the sign-in submit button
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, SUBMIT_LOGIN_XPATH))
        ).click()

        # Wait for login success element to appear
        try:
            mydaft_btn = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, LOGIN_SUCCESS_XPATH))
            )
            if "MyDaft" not in mydaft_btn.text:
                raise DaftRentalBotLoginError(
                    "Incorrect username or password. Please try again."
                )
        except Exception:
            raise DaftRentalBotLoginError(
                "Incorrect username or password. Please try again."
            )

        print("Logged in successfully!")


class Apply(SetUp):
    applied = []
    def apply(self):
        self.login()
        generate_link = GenerateLink()
        self.link = generate_link.generate_filter_link()

        # Run automation for this interval of time
        end_time = generate_end_time()

        while time.time() < end_time:
            try:
                self.driver.get(self.link)
                # Click the latest ad on the page.
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, LATEST_AD_XPATH))).click()

                sleep(1)  # Wait for 1 second to ensure the page loads

                if self.driver.current_url not in self.applied:
                    self.applicationProcess()
                    self.applied.append(self.driver.current_url)
                else:
                    print("Already applied for this house.")
                
                sleep(30)  # Wait for 30 seconds before applying for the next one
            except Exception as e:
                print("Some error occurred: ", e)
                # Wait for 2 minutes before applying for the next one
                print("Waiting for 2 minutes before applying for the next one...")
                sleep(120)

        print("Finishing up the process!")

        self.driver.quit()
        self.file.close()

    def checkFeedback(self):
        # Check if there is a feedfack form on the page
        try:
            # Click on close feedback if exists
            self.driver.find_element(By.XPATH, FEEDBACK_CLOSE_XPATH).click()
        except:
            print("Feedback form had popped up! I took care of it.")

    def applicationProcess(self):
        log_address = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, ADDRESS_XPATH))
        ).text

        log_price = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, PRICE_XPATH))
        ).text

        log_price = "EUR " + log_price[1:]

        log_entry = [log_price, log_address, self.driver.current_url, "Applied"]

        # click on the link that opens a new window
        self.driver.switch_to.active_element
        # Fill the application in pop-up
        # Click on email_button
        self.driver.find_element(By.XPATH, EMAIL_BUTTON_XPATH).click()
        sleep(3)
        self.checkFeedback()
        # Enter First Name
        # self.driver.find_element(By.XPATH, FIRSTNAME_FIELD_XPATH).send_keys(self.SECRET_FNAME)
        # self.checkFeedback()
        # Enter Last Name
        # self.driver.find_element(By.XPATH, LASTNAME_FIELD_XPATH).send_keys(self.SECRET_LNAME)
        # self.checkFeedback()
        # Enter Email-ID
        # self.driver.find_element(By.XPATH, EMAILID_FIELD_XPATH).send_keys(self.SECRET_ID)
        # self.checkFeedback()
        # Enter Contact Number
        # self.driver.find_element(By.XPATH, CONTACT_FIELD_XPATH).send_keys(self.SECRET_CONTACT)
        # Set number of people to 2
        self.driver.find_element(By.XPATH, PEOPLE_INCREAMENT_BUTTON_XPATH).click()
        # Select No Pets
        self.driver.find_element(By.XPATH, NO_PET_RADIO_XPATH).click()
        self.checkFeedback()

        # Enter Application text
        # self.driver.find_element(By.XPATH, MESSAGE_FIELD_XPATH).send_keys(self.SECRET_MESSAGE)
        # self.checkFeedback()

        # Send the applicaiton
        self.driver.find_element(By.XPATH, SEND_APPLICATION_XPATH).click()
        sleep(2)

        self.checkFeedback()

        # Close the window
        self.driver.find_element(By.XPATH, CLOSE_MODAL_XPATH).click()

        self.checkFeedback()

        try:
            # Check if already applied
            text = self.driver.find_element(By.XPATH, ALREADY_APPLIED_XPATH).text
            if text == "Sorry, something went wrong.":
                print("Already applied for this house!")
        except:
            self.writer.writerow(log_entry)
            print("Applied for a house!")
        # Wait 10 seconds till you apply for the next one
        sleep(10)


run = Apply()
run.apply()
