# screenshot.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import time
from urllib.parse import urlparse

def take_screenshot(url, filename=None):
    # Parse the URL and keep only scheme + netloc (root domain)
    parsed = urlparse(url)
    root_url = f"{parsed.scheme}://{parsed.netloc}"

    # Get the absolute path to this file's directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Path for static/screenshots inside project
    static_folder = os.path.join(BASE_DIR, "static", "screenshots")
    os.makedirs(static_folder, exist_ok=True)

    # Filename
    if filename is None:
        filename = f"screenshot_{int(time.time())}.png"

    screenshot_path = os.path.join(static_folder, filename)

    # Selenium options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--force-device-scale-factor=1")
    options.add_argument("--high-dpi-support=1")

    service = Service()
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(root_url)  # Navigate to the root domain only
        time.sleep(3)  # wait for page load

        # Remove pop-ups or overlays
        driver.execute_script("""
            const selectors = [
                '[id*="popup"]','[class*="popup"]','[id*="cookie"]','[class*="cookie"]',
                '[id*="overlay"]','[class*="overlay"]','[id*="consent"]','[class*="consent"]',
                '[id*="subscribe"]','[class*="subscribe"]',
                '[id*="captcha"]','[class*="captcha"]',
                '[id*="recaptcha"]','[class*="recaptcha"]',
                '[id*="hcaptcha"]','[class*="hcaptcha"]',
                'iframe[src*="recaptcha"]','iframe[src*="hcaptcha"]'
            ];
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => {
                    el.style.display='none';
                });
            });
        """)

        time.sleep(1)
        driver.save_screenshot(screenshot_path)

        # Return relative path so Flask can serve it
        return f"screenshots/{filename}"

    finally:
        driver.quit()





