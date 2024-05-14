# newegg_module.py
import asyncio
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from BotSettings import settings, xPaths


class AutoBot:
    def __init__(self, profile, product_url, password):
        self.profile = profile
        self.product_url = product_url
        self.password = password
        self.driver = None
        self.wait = None

    def setup_driver(self):
        service = Service(executable_path=settings["DRIVER"])
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    async def start_session(self):
        print("Logging in...")
        self.driver.get("https://www.newegg.com/")
        if settings["SKIPSIGNIN"]:
            return True
        self.driver.find_element(By.XPATH, xPaths["signIn"]).click()
        self.wait.until(EC.visibility_of_element_located((By.NAME, "signEmail"))).send_keys(self.profile["Email"])
        self.driver.find_element(By.NAME, "signIn").click()
        self.wait.until(EC.visibility_of_element_located((By.NAME, "password"))).send_keys(self.password)
        self.driver.find_element(By.NAME, "signIn").click()
        try:
            welcome_element = self.wait.until(EC.visibility_of_element_located((By.XPATH, xPaths["welcomeText"])))
            if "Welcome" in welcome_element.text:
                print("Logged in successfully.")
                return True
        except TimeoutException:
            print("Login failed or timeout reached.")
            return False

    async def navigate_and_add_to_cart(self):
        print("Navigating to product page and adding to cart...")
        self.driver.get(self.product_url)
        add_to_cart_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, xPaths["addToCart"])))
        add_to_cart_button.click()
        try:
            proceedToCheckout = self.wait.until(EC.element_to_be_clickable((By.XPATH, xPaths["noThanks"])))
            proceedToCheckout.click()
            print("Item added to cart.")
        except TimeoutException:
            print("Failed to add item to cart.")

    async def proceed_through_checkout(self):
        print("Continuing to delivery...")
        try:
            continue_to_delivery_button = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, xPaths["continueToDeliveryButton"])))
            continue_to_delivery_button.click()
            print("Continue to delivery button clicked.")
        except TimeoutException:
            print("Failed to click on 'Continue to Delivery' button. Retrying...")
            # Add more debug information to understand what's happening
            try:
                element = self.driver.find_element(By.XPATH, xPaths["continueToDeliveryButton"])
                print(f"Element found: {element}")
            except Exception as e:
                print(f"Element not found: {e}")
            return

        # Adding a 4-second wait after clicking the "Proceed to Checkout" button
        print("Waiting for 4 seconds to load...")
        time.sleep(4)

        print("Checking for Place Order button...")
        try:
            place_order_button = self.wait.until(EC.presence_of_element_located((By.XPATH, xPaths["placeOrderButton"])))
            print("Place Order button found. Entering CVV and proceeding with new method.")

            # Adding a 4-second wait before entering the CVV
            print("Waiting for 4 seconds before entering CVV...")
            time.sleep(4)

            try:
                new_cvv_input = self.wait.until(EC.element_to_be_clickable((By.XPATH, xPaths["newCVVInput"])))
                new_cvv_input.click()
                print("New CVV input field clicked.")
                new_cvv_input.send_keys(self.profile["CVV"])
                print("New CVV entered successfully.")

                # Scroll down to make the "Place Order" button visible
                self.driver.execute_script("arguments[0].scrollIntoView();", place_order_button)
                print("Scrolled to Place Order button.")

                # Wait for the button to be clickable and then click it
                final_place_order_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, xPaths["finalPlaceOrderButton"])))
                final_place_order_button.click()
                print("Final Place Order button clicked.")

                # Click the last button again
                try:
                    summary_place_order_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, xPaths["summaryPlaceOrderButton"])))
                    summary_place_order_button.click()
                    print("Summary Place Order button clicked.")
                except TimeoutException:
                    print("Summary Place Order button not found.")
            except TimeoutException:
                print("New CVV input field not found or not available in time.")
        except TimeoutException:
            print("Place Order button not found. Trying old method.")

            # Adding a 4-second wait before entering the CVV
            print("Waiting for 4 seconds before entering CVV...")
            time.sleep(4)

            try:
                old_cvv_input = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH,
                     "//*[@id='paymentItemCell']/div/div[2]/div/div[3]/div[2]/div[3]/div[1]/div/label/div[4]/input")))
                old_cvv_input.click()
                print("Old CVV input field clicked.")
                old_cvv_input.send_keys(self.profile["CVV"])
                print("Old CVV entered successfully.")
                review_order_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, xPaths["reviewOrderButton"])))
                review_order_button.click()
                print("Review Order button clicked.")
            except TimeoutException:
                print("Old CVV input field not found or not available in time.")

        print("Letting it load...")
        time.sleep(3)  # Wait for the order to process and any confirmation screens

        try:
            finalize_payment_button = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, xPaths["finalPlaceOrderButton"])))
            finalize_payment_button.click()
            print("Final Place Order Button Clicked")
        except TimeoutException:
            print("Item purchased.")
            return
        await self.check_success()

    async def check_success(self):
        print("Waiting for potential confirmation...")
        time.sleep(3)  # Wait for any final page transitions
        try:
            confirmation_element = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id='app']/div[2]/section/div/a/span")))
            if confirmation_element:
                print("Purchase confirmed successfully!")
            else:
                print("Confirmation element not found, check for possible issues.")
        except TimeoutException:
            print("No confirmation element found within the timeout period.")

    async def start_bot(self):
        self.setup_driver()
        if await self.start_session():
            await self.navigate_and_add_to_cart()
            await self.proceed_through_checkout()
            print("Bot operations completed successfully.")
        else:
            print("Session failed to start.")
        self.driver.quit()
