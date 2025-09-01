from checking import check_website
from ssl_check import get_ssl_expiry_date
from broken_links import check_broken_links
from logger import log_info, log_error
from urllib.parse import urlparse
from datetime import datetime
from storing import save_to_csv, save_broken_links
from screenshot import take_screenshot
from mobile_friendly import check_mobile_friendly

def calculate_score(load_time, page_size, ssl_days, broken_count, was_redirected):
    score = 0

    if load_time < 1:
        score += 25
    elif load_time < 2:
        score += 20
    elif load_time < 3:
        score += 15
    elif load_time < 4:
        score += 10
    else:
        score += 5

    if page_size < 500:
        score += 15
    elif page_size < 1000:
        score += 10
    else:
        score += 5


    if ssl_days > 180:
        score += 20
    elif ssl_days > 90:
        score += 15
    elif ssl_days > 30:
        score += 10
    elif ssl_days > 0:
        score += 5
    else:
        score += 0

    
    if broken_count == 0:
        score += 20
    elif broken_count < 3:
        score += 15
    elif broken_count < 6:
        score += 10
    else:
        score += 5

    
    score += 10 if not was_redirected else 5

    return score


url = input("Enter the URL (include https://): ")
if not url.startswith("http"):
    url = "https://" + url

try:
    data = check_website(url)

    if "error" in data:
        print("Error:", data["error"])
    else:
        print(f"\n ▸ URL: {data['url']}")
        print(f" ▸ Status Code: {data['status_code']} - {data['status_message']}")
        print(f" ▸ Response Time: {data['load_time']} seconds")
        print(f" ▸ Performance: {data['performance']}")
        print(f" ▸ Page Size: {data['page_size_kb']} KB")
        print(f" ▸ Content-Type: {data['content_type']}")
        print(f" ▸ Server: {data['server']}")
        print(f" ▸ Content-Encoding: {data['content_encoding']}")
        print(f" ▸ Cache-Control: {data['cache_control']}")

        #  Redirect info
        if data.get("was_redirected"):
            print("\n ▸ Redirect Detected!")
            print(f" ▸ Redirect Status Code: {data['redirect_status_code']}")
            print(f" ▸ Redirect Target: {data['redirect_target']}")

        log_info(f"{url} checked successfully")

        #  SSL Check
        hostname = urlparse(url).hostname
        ssl_expiry = get_ssl_expiry_date(hostname)
        days_left = (ssl_expiry - datetime.now()).days
        print(f"\n ▸ SSL Expiry Date: {ssl_expiry.date()} ({days_left} days left)")

        #  Broken Links Check
        broken_links = check_broken_links(url)
        broken_count = len(broken_links)
        if broken_links:
            print(f"\n ▸ Broken links found! ({broken_count})")
        else:
            print("\n ▸ No broken links found.")
        save_broken_links(broken_links)

        #  Mobile-friendliness check
        mobile_result = check_mobile_friendly(url)

        if mobile_result["is_mobile_friendly"]:
            print("\n ▸ Mobile-Friendly:  Yes")
        else:
            print("\n ▸ Mobile-Friendly: No")
            for issue in mobile_result["issues"]:
                print(f"   - Issue: {issue}")


        #  Performance Score
        score = calculate_score(
            load_time=data['load_time'],
            page_size=data['page_size_kb'],
            ssl_days=days_left,
            broken_count=broken_count,
            was_redirected=data.get('was_redirected', False)
        )
        print(f"\n ▸ Overall Performance Score: {score}/100")

        # Screenshot
        take_screenshot(url)

        # Store result
        result = {
            'url': data['url'],
            'status_code': data['status_code'],
            'status_message': data['status_message'],
            'load_time': data['load_time'],
            'performance': data['performance'],
            'page_size_kb': data['page_size_kb'],
            'content_type': data['content_type'],
            'server': data['server'],
            'content_encoding': data['content_encoding'],
            'cache_control': data['cache_control'],
            'ssl_expiry': ssl_expiry.date(),
            'ssl_days_left': days_left,
            'was_redirected': data.get('was_redirected'),
            'redirect_status_code': data.get('redirect_status_code'),
            'redirect_target': data.get('redirect_target'),
            'mobile_friendly': mobile_result["is_mobile_friendly"],
            'mobile_issues': "; ".join(mobile_result["issues"]),
            'broken_links_count': broken_count,
            'score': score
        }

        save_to_csv(result)

except Exception as e:
    log_error(f"Unhandled error: {e}")
    print("An unexpected error occurred. Check the logs for more details.")





