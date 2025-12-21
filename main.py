import json
import os
import asyncio
from datetime import datetime, timedelta
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from dotenv import load_dotenv
import re
from booking_attempt import BookingAttempt

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")

class AutoBooker:
    def __init__(self):
        load_dotenv()
        self.email = os.getenv("EMAIL", "")
        self.password = os.getenv("PASSWORD", "")

    @staticmethod
    def get_config():
        with open(config_path, "r") as f:
            return json.load(f)

    @staticmethod
    def get_next_date(target_day: str, target_time: str) -> str:
        # calculate the next occurence of the target day
        days = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}
    
        today = datetime.now().date()
        target_day = days[target_day.lower()]
        target_time_obj = datetime.strptime(target_time, "%H:%M").time()
        now_time = datetime.now().time()

        if today.weekday() == target_day and target_time_obj < now_time:
            target_date = today + datetime.timedelta(days=7)
            return target_date.strftime('%Y-%m-%d')
        
        days_ahead = (target_day - today.weekday() + 7) % 7
        target_date = today + datetime.timedelta(days=days_ahead)
        return target_date.strftime('%Y-%m-%d')

    async def launch_browser(self, headless: bool = False):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=headless)
        self.context = await self.browser.new_context()
        print("Broswer launched")

    async def create_page(self) -> Page:
        page = await self.context.new_page()
        return page

    async def accept_cookies(self, page: Page):
        try:
            await page.wait_for_selector("text=Accept All Cookies")
            await page.get_by_role("button", name="Accept All Cookies").click()
            print("cookies accepted")
        except Exception as e:
            print("ERROR: Could not click cookies")
            return "Error"

    async def login(self, page: Page):
        try:
            login_url = "https://myaccount.better.org.uk/login?redirect=/"
            await page.goto(login_url)

            await self.accept_cookies(page)

            # fill in page
            await page.get_by_role("textbox", name="Email address or customer ID").fill(self.email)
            await page.get_by_role("textbox", name="Password").fill(self.password)
            await page.get_by_test_id("log-in").click()

            # Wait for login success
            for _ in range(20):
                if await page.query_selector('a[data-testid="my-account"]') or \
                   await page.query_selector('div.AccountMenu__Wrapper-sc-1v5z2hj-0'):
                    print("✓ Login successful")
                    return True
                await asyncio.sleep(1)
            
            print("Login failed")
            return False
        except Exception as e:
            print(f"Login error: {e}")
            return False

    async def clear_basket(self, page: Page):
        try:
            await page.wait_for_timeout(2000)

            while True:
                remove_buttons = page.get_by_test_id("basketRemoveButton")
                count = await remove_buttons.count()

                if count == 0:
                    break

                await remove_buttons.first.click()
                await asyncio.sleep(0.5)

            print("Basket cleared")
        except Exception as e:
            print(f"Basket already empty or error: {e}")

