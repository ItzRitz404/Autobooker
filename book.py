from dotenv import load_dotenv
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import json
from datetime import datetime, timedelta
from add_basket import add_to_basket
from scheduler import schedule, start_scheduler

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")

def get_config():
        with open(config_path, "r") as f:
            return json.load(f)

def get_next_date(target_day: str, target_time: str) -> str:
        # calculate the next occurence of the target day
        days = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }

        today = datetime.now().date()
        target_day = days[target_day.lower()]
        target_time_obj = datetime.strptime(target_time, "%H:%M").time()
        now_time = datetime.now().time()

        if today.weekday() == target_day and target_time_obj < now_time:
            target_date = today + timedelta(days=7)
            return target_date.strftime("%Y-%m-%d")

        days_ahead = (target_day - today.weekday() + 7) % 7
        target_date = today + timedelta(days=days_ahead)
        return target_date.strftime("%Y-%m-%d")
        
# options.add_argument("--headless")
def login(driver):
    driver.get("https://myaccount.better.org.uk/login?redirect=/")

    wait = WebDriverWait(driver, 15)

    load_dotenv()

    print(os.getenv("EMAIL", ""))
    cookie_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div[2]/div/div/div[3]/button"))
    )
    cookie_btn.click()


    email = wait.until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/div/div/form/div[1]/div/input"))
    )

    email.send_keys(os.getenv("EMAIL", ""))

    password = wait.until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/div/div/form/div[2]/div/div/input"))
    )

    password.send_keys(os.getenv("PASSWORD", ""))

    login_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/div/div/form/div[3]/button/span"))
    )
    login_btn.click()

    wait.until(
    EC.text_to_be_present_in_element(
        (By.XPATH, "/html/body/div[1]/main/div/div/div[1]/div[1]/div[2]"),  # locator of element
        "Customer no: BET6615079"         # text to wait for
    )
)
    # time.sleep(10)  

def court_booking(option):
    # location = automation_dets["location"]
    # activity = automation_dets["activity"]
    # target_times = automation_dets["time"].split("-")[0]
    # date = self.get_next_date(automation_dets["day"], target_times)
    # time_slot = automation_dets["time"]
    # courtnum = automation_dets["court_number"]
    
    location = option["location"]
    activity = option["activity"]
    target_times = option["time"].split("-")[0]
    date =  get_next_date(option["day"], target_times)
    time_slot = option["time"]
    courtnum = option["court_number"]
    
    courtbooking = f"https://bookings.better.org.uk/location/{location}/{activity}/{date}/by-location/slot/{time_slot}/6yuu8jj0/{courtnum}"
    
    return courtbooking

def click_element(driver, element_xpath):
    wait = WebDriverWait(driver, 15)
    element = wait.until(
        EC.element_to_be_clickable((By.XPATH, element_xpath))
    )
    element.click()

def run_login(driver):
    login(driver)
    
    
def run_booking_process(driver):
    
    config = get_config()
    # print(config)
    
    for idx, option in enumerate(config):
        # print(f"Option {idx}: {option}")
            
        driver.get(court_booking(option))       
        
        # click_element(driver, "/html/body/div[7]/div[3]/div[2]/button[2]")
        if add_to_basket(driver, "/html/body/div[7]/div[3]/div[2]/button[2]"):
            print(f"Successfully added booking id={option.get('id', '??')} to basket.")
        else:
            print(f"Failed to add booking id={option.get('id', '??')} to basket.")
        # time.sleep(10)
        
    driver.get("https://bookings.better.org.uk/basket/checkout")
    
    click_element(driver, "/html/body/div[1]/main/div/div/div[1]/div/div/div[3]/div[2]/div/button")
    
    wait = WebDriverWait(driver, 15)
    tc = wait.until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/div/div/div[1]/div/div/div[4]/div/div/form/div[1]/div/div/label/div[1]/span/span/input"))
    )
    
    tc.is_selected() 
    
    if not tc.is_selected():
        tc.click()
        
    click_element(driver, "/html/body/div[1]/main/div/div/div[1]/div/div/div[4]/div/div/form/div[2]/button")
    
    time.sleep(10)
    
if __name__ == "__main__":
    # run_booking_process()
    
    # print(config)
    
    options = Options()
    driver = webdriver.Chrome(options=options)
    
    schedule(
        hour=21,
        minute=55,
        seconds=00,
        fuc=run_login,
        args=[driver]
    )
    
    schedule(
        hour=21,
        minute=59,
        seconds=57,
        fuc=run_booking_process,
        args=[driver]
    )
    
    start_scheduler()