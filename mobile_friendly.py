from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import time

def check_mobile_friendly(url, timeout=10):
    mobile_width = 375
    mobile_height = 812

    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"--window-size={mobile_width},{mobile_height}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")


    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(timeout)
        driver.get(url)
        time.sleep(3)

        result = {
            "is_mobile_friendly": True,
            "issues": []
        }

        # ✅ Check for viewport meta tag
        metas = driver.find_elements(By.TAG_NAME, "meta")
        viewport_found = any(
            (meta.get_attribute("name") or "").lower() == "viewport"
            for meta in metas
        )
        if not viewport_found:
            result["is_mobile_friendly"] = False
            result["issues"].append("Missing viewport meta tag.")

        # ✅ Check for horizontal scroll
        scroll_width = driver.execute_script("return document.body.scrollWidth")
        client_width = driver.execute_script("return document.documentElement.clientWidth")
        if scroll_width > client_width:
            result["is_mobile_friendly"] = False
            result["issues"].append(
                f"Horizontal scroll detected ({scroll_width}px > {client_width}px)."
            )

        return result

    except WebDriverException as e:
        return {
            "is_mobile_friendly": False,
            "issues": [f"Selenium error: {str(e)}"]
        }
    except Exception as e:
        return {
            "is_mobile_friendly": False,
            "issues": [f"Unexpected error: {str(e)}"]
        }
    finally:
        if driver:
            driver.quit()


