import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import re
import time

# def add_to_basket(driver, element_xpath ):
#     try:
#         wait = WebDriverWait(driver, 15)
        
        
#         print("Page loaded, looking for price text")
#         wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[7]/div[3]/div[1]/div/div[2]/div[4]/span")))
#         print("Price text located, looking for add to basket button")
        
#         element = wait.until(
#             EC.presence_of_element_located((By.XPATH, element_xpath))
#         )
#         print("Located the add to basket button")
        
#         # time.sleep(10)  # small delay to ensure the element state is updated
#         if element.get_attribute("disabled"):
#             print("Button is disabled")
#             return False
        
#         print("checking if button is clickable")
#         element = wait.until(
#             EC.element_to_be_clickable((By.XPATH, element_xpath))
#         )
#         print("Button is clickable")

#         # print("Button is enabled")
        
#         element.click()
#         return True
#     except Exception as e:
#         print(f"Failed to add to basket: {e}")
    
#     return False
    
    
def add_to_basket(driver, element_xpath, timeout=15):
    wait = WebDriverWait(driver, timeout)

    try:
        # 1️⃣ Wait for price text to appear (visible, not just present)
        print("Waiting for price text...")
        price_locator = (By.XPATH, "/html/body/div[7]/div[3]/div[1]/div/div[2]/div[4]/span")
        wait.until(EC.visibility_of_element_located(price_locator))
        print("Price text located.")

        # 2️⃣ Wait for the add-to-basket button to be visible
        print("Looking for add-to-basket button...")
        button_locator = (By.XPATH, element_xpath)
        button = wait.until(EC.visibility_of_element_located(button_locator))

        # 3️⃣ Wait until the button is clickable
        print("Waiting for button to be clickable...")
        button = wait.until(EC.element_to_be_clickable(button_locator))

        # 4️⃣ Optional: check if button is disabled via attribute or class
        disabled = button.get_attribute("disabled") or "disabled" in button.get_attribute("class")
        if disabled:
            print("Button is disabled.")
            return False

        # 5️⃣ Click the button
        print("Clicking the button...")
        button.click()
        print("Button clicked successfully.")
        return True

    except TimeoutException:
        print("Element not found or not clickable within timeout.")
    except StaleElementReferenceException:
        print("Button was replaced in DOM. Retry the function.")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return False
