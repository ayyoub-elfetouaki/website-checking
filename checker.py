from checking import check_website
from ssl_check import get_ssl_expiry_date
from broken_links import check_broken_links
from storing import save_to_csv, save_broken_links
from screenshot import take_screenshot
from mobile_friendly import check_mobile_friendly
from logger import log_info, log_error
from urllib.parse import urlparse
from datetime import datetime


def run_checks(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    results = {}
    try:
        # Main website check
        website_data = check_website(url)
        results["website"] = website_data

        # SSL expiry date
        results["ssl_expiry"] = get_ssl_expiry_date(url)

        # Broken links
        results["broken_links"] = check_broken_links(url)

        # Screenshot
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace(".", "_")
        screenshot_filename = f"screenshot_{domain}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        take_screenshot(url, screenshot_filename)
        results["screenshot"] = screenshot_filename

        # Mobile friendly
        results["mobile_friendly"] = check_mobile_friendly(url)

        # Save results to CSV
        save_to_csv(
            url,
            website_data["status_code"],
            website_data["load_time"],
            results["ssl_expiry"]
        )
        save_broken_links(url, results["broken_links"])

        log_info(f"Successfully checked {url}")

    except Exception as e:
        log_error(f"Error checking {url}: {e}")
        results["error"] = str(e)

    return results


