import requests
from http import HTTPStatus
from ssl_check import get_ssl_expiry_date
from broken_links import check_broken_links
from screenshot import take_screenshot
from mobile_friendly import check_mobile_friendly
from urllib.parse import urlparse
from datetime import datetime

def check_website(url):
    results = {
        "url": url
    }

    try:
        # --- BASIC WEBSITE CHECK ---
        initial_response = requests.get(url, allow_redirects=False, timeout=10)
        final_response = requests.get(url, timeout=10)

        results["status_code"] = final_response.status_code
        results["status_message"] = HTTPStatus(final_response.status_code).phrase
        results["load_time"] = round(final_response.elapsed.total_seconds(), 2)
        results["page_size_kb"] = round(len(final_response.content) / 1024, 2)
        results["performance"] = "Good" if results["load_time"] < 1 else "Moderate" if results["load_time"] < 3 else "Slow"

        results["content_type"] = final_response.headers.get("Content-Type", "N/A")
        results["server"] = final_response.headers.get("Server", "N/A")
        results["content_encoding"] = final_response.headers.get("Content-Encoding", "N/A")
        results["cache_control"] = final_response.headers.get("Cache-Control", "N/A")

        results["was_redirected"] = initial_response.status_code in (301, 302, 303, 307, 308)
        results["redirect_status_code"] = initial_response.status_code if results["was_redirected"] else None
        results["redirect_target"] = initial_response.headers.get("Location") if results["was_redirected"] else None

    except requests.RequestException as e:
        results["error"] = f"Website request failed: {e}"
        return results  # Stop here if even basic check fails

    # --- SSL CHECK ---
    try:
        expiry_date, days_left = get_ssl_expiry_date(url)
        results["ssl_expiry_date"] = expiry_date
        results["ssl_days_left"] = days_left
    except Exception as e:
        results["ssl_error"] = str(e)

    # --- BROKEN LINKS CHECK ---
    try:
        results["broken_links"] = check_broken_links(url)
    except Exception as e:
        results["broken_links_error"] = str(e)

    # --- SCREENSHOT ---
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace(".", "_")
        screenshot_filename = f"screenshot_{domain}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        take_screenshot(url, screenshot_filename)
        results["screenshot"] = screenshot_filename
    except Exception as e:
        results["screenshot_error"] = str(e)

    # --- MOBILE FRIENDLY CHECK ---
    try:
        results["mobile_friendly"] = check_mobile_friendly(url)
    except Exception as e:
        results["mobile_friendly_error"] = str(e)

    return results


