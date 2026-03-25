import json
import os
import asyncio
from datetime import datetime, time, timedelta
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

# from dotenv import load_dotenv
from dotenv import load_dotenv
import re
from booking_attempt import Booking

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

    # async def launch_browser(self, headless: bool = False):
    async def launch_browser(self, headless: bool = False):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.context = await self.browser.new_context()
        print("Browser launched")

    async def close(self):
        try:
            await self.context.close()
        except Exception:
            pass
        try:
            await self.browser.close()
        except Exception:
            pass
        try:
            await self.playwright.stop()
        except Exception:
            pass

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
            return False

    async def login(self, page: Page):
        try:
            login_url = "https://myaccount.better.org.uk/login?redirect=/"
            await page.goto(login_url)

            await self.accept_cookies(page)

            # fill in page
            await page.get_by_role("textbox", name="Email address or customer ID").fill(
                self.email
            )
            await page.get_by_role("textbox", name="Password").fill(self.password)
            await page.get_by_test_id("log-in").click()

            # Wait for login success
            for _ in range(20):
                if await page.query_selector(
                    'a[data-testid="my-account"]'
                ) or await page.query_selector("div.AccountMenu__Wrapper-sc-1v5z2hj-0"):
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

            return True
        except Exception as e:
            print(f"Basket already empty or error: {e}")
            return False

    async def wait_for_activation_time(self, activation_time: str) -> None:
        today = datetime.now().date()
        target_t = datetime.strptime(activation_time, "%H:%M:%S").time()
        target_dt = datetime.combine(today, target_t)
        print("Waiting for activation time:", target_dt)

        now = datetime.now()
        if now >= target_dt:
            return

        while True:
            now = datetime.now()
            remaining = (target_dt - now).total_seconds()
            if remaining <= 0:
                break

            await asyncio.sleep(min(0.5, max(0.05, remaining)))

    async def navigate_to_page(self, page: Page, automation_dets):
        location = automation_dets["location"]
        activity = automation_dets["activity"]
        target_times = automation_dets["time"].split("-")[0]
        date = self.get_next_date(automation_dets["day"], target_times)
        time_slot = automation_dets["time"]
        court = automation_dets["court_number"]

        url = f"https://bookings.better.org.uk/location/{location}/{activity}/{date}/by-location/slot/{time_slot}/6yuu8jj0/{court}"

        try:
            # await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            # await page.wait_for_load_state("networkidle", timeout=45000)
            await page.goto(url)
            print(f"Navigated to {url}")
            return True
        except Exception as e:
            print(f"Error navigating to {url}: {e}")
            return False
        


    async def book_activity(self, page: Page):
        try:
            # await page.wait_for_selector("text=Date:")

            court_msg = await page.get_by_text(
                re.compile("You are ineligible to book|No slot available", re.I)
            ).is_visible()
            print("court_msg:", court_msg)

            if court_msg:
                print("No court available to book")
                return "No court"

            # Add to basket               
            await page.get_by_role("button", name="Add to basket").click()
            print("Activity added to basket")
            return True
        except Exception as e:
            print(f"Error adding activity to basket: {e}")
            return False

    async def proceed_to_checkout(self, page: Page):
        try:
            await page.goto("https://bookings.better.org.uk/basket/checkout")
            print("Proceeded to checkout")
            return True
        except Exception as e:
            print(f"Error proceeding to checkout: {e}")
            return False

    async def credit_manager(self, page: Page):
        try:
            await page.wait_for_selector(":text('Checkout')")
            print("At checkout page")
            await page.wait_for_timeout(2000)

            credit = await page.get_by_text(
                re.compile("Pay full amount using credit|Use full credit balance", re.I)
            ).is_visible()
            print("credit_button:", credit)

            if not credit:
                print("No credit option available")
                return False

            credit_button = page.get_by_role(
                "button",
                name=re.compile(
                    "Pay full amount using credit|Use full credit balance", re.I
                ),
            )

            await credit_button.click()
            print("Credit applied")
            return True

        except Exception as e:
            print(f"No credit to apply or error: {e}")
            return False

    async def check_terms(self, page: Page):
        try:
            check = page.get_by_role("checkbox", name="I agree to the  Terms and")
            await check.check()
            print("Terms agreed")
            return True
        except Exception as e:
            print(f"Error agreeing to terms: {e}")
            return False

    async def confirm_booking(self, page: Page):
        try:
            cfm = page.get_by_role("button", name="Pay now")
            await cfm.click()
            print("Booking confirmed")
            return True
        except Exception as e:
            print(f"Error confirming booking: {e}")
            return False
        

    async def run(self, automation, activation_time, headless: bool = False):

        page = None
        checkout_page = None
        pages = []

        if isinstance(automation, dict):
            automations = [automation]
        elif isinstance(automation, list):
            automations = automation
        else:
            raise TypeError(
                f"automation must be dict or list[dict], got: {type(automation)}"
            )

        try:
            # Launch browser
            await self.launch_browser(headless=headless)

            # Create main page for login and clear booking
            page = await self.create_page()
            
            async def block_heavy(route):
                t = route.request.resource_type
                if t in ("image", "font", "media"):
                    await route.abort()
                else:
                    await route.continue_()

            await self.context.route("**/*", block_heavy)

            is_login = await self.login(page)
            if not is_login:
                print("Login failed, exiting")
                return False

            # Clear basket
            await self.clear_basket(page)

            # # Create checkout page
            # checkout_page = await self.create_page()

            # Wait for activation time
            await self.wait_for_activation_time(activation_time)

            for a in automations:
                p = await self.create_page()
                pages.append(p)
                await self.navigate_to_page(p, a)
                await self.book_activity(p)

            # # await asyncio.sleep(1)  #
            # Create checkout page
            checkout_page = await self.create_page()

            # Proceed to checkout
            await self.proceed_to_checkout(checkout_page)

            # Apply credit
            await self.credit_manager(checkout_page)

            # Agree to terms
            await self.check_terms(checkout_page)

            # Confirm booking
            await self.confirm_booking(checkout_page)
            print("Booking process completed")
            
            await page.wait_for_timeout(10000)  # wait 10 seconds to see result

            return True
        except Exception as e:
            print(f"Error during booking process: {e}")
            return False
        finally:
            for p in pages:
                try:
                    await p.close()
                except Exception:
                    pass
            if checkout_page:
                try:
                    await checkout_page.close()
                except Exception:
                    pass
            if page:
                try:
                    await page.close()
                except Exception:
                    pass

            await self.close()

    # async def run(self, automations: list[dict], activation_time: str, headless: bool = False):
    #     page = None
    #     checkout_page = None
    #     pages = []

    #     if not isinstance(automations, list):
    #         raise TypeError(f"automations must be list[dict], got {type(automations)}")
    #     if not automations:
    #         print("No automations provided")
    #         return False

    #     try:
    #         await self.launch_browser(headless=headless)

    #         page = await self.create_page()
    #         if not await self.login(page):
    #             print("Login failed, exiting")
    #             return False

    #         await self.clear_basket(page)

    #         await self.wait_for_activation_time(activation_time)

    #         # one page per automation
    #         for a in automations:
    #             p = await self.create_page()
    #             pages.append(p)
    #             await self.navigate_to_page(p, a)
    #             await self.book_activity(p)

    #         checkout_page = await self.create_page()
    #         await self.proceed_to_checkout(checkout_page)
    #         await self.credit_manager(checkout_page)
    #         await self.check_terms(checkout_page)
    #         await self.confirm_booking(checkout_page)

    #         print("Booking process completed")
    #         return True

    #     except Exception as e:
    #         print(f"Error during booking process: {e}")
    #         return False

    #     finally:
    #         for p in pages:
    #             try:
    #                 await p.close()
    #             except Exception:
    #                 pass
    #         if checkout_page:
    #             try:
    #                 await checkout_page.close()
    #             except Exception:
    #                 pass
    #         if page:
    #             try:
    #                 await page.close()
    #             except Exception:
    #                 pass
    #         await self.close()

    # async def test_runner(self, headless: bool = False):
    #     cfg = self.get_config()
    #     automation = next(a for a in cfg if a.get("enabled", True))
    #     activation = automation.get("activation_time")

    #     await self.run(automation, activation, headless=headless)

    # await self.launch_browser(headless=headless)

    # page = await self.create_page()

    # ok = await self.login(page)
    # print("login ok?", ok)
    # if not ok:
    #     await self.close()
    #     return
    # # await page.pause()
    # await self.clear_basket(page)
    # control = await self.create_page()
    # # await self.wait_for_activation_time(activation)
    # await self.navigate_to_page(page, automation)
    # await self.book_activity(page)

    # await self.proceed_to_checkout(control)
    # await self.credit_manager(control)
    # await self.check_terms(control)
    # await self.confirm_booking(control)
    # # pause so you can visually inspect if headless=False
    # await page.wait_for_timeout(5000)

    # await self.close()


if __name__ == "__main__":

    async def main():
        bot = AutoBooker()
        cfg = bot.get_config()
        # automation = [a for a in cfg if a.get("enabled", True)]
        # activation = automation.get("activation_time")

        for a in cfg:
            activation = a.get("activation_time")

            await bot.run(a, activation, headless=False)

    asyncio.run(main())
