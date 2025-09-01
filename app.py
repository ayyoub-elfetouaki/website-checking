from flask import Flask, render_template, request, redirect, url_for, session
from checking import check_website
from ssl_check import get_ssl_expiry_date
from broken_links import check_broken_links
from screenshot import take_screenshot
from mobile_friendly import check_mobile_friendly
from storing import save_to_csv, save_broken_links
from logger import log_info, log_error
from urllib.parse import urlparse
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "super_secret_key_123"  

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

# -----------------------------
# Routes
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url", "").strip()

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        results = {}
        try:
            log_info(f"Starting check for: {url}")

            # Website Check
            website_data = check_website(url)
            if "error" in website_data:
                raise Exception(website_data["error"])
            results.update(website_data)

            # SSL Check
            hostname = urlparse(url).hostname
            ssl_expiry = get_ssl_expiry_date(hostname)
            if ssl_expiry:
                results["ssl_expiry_date"] = ssl_expiry.strftime("%Y-%m-%d")
                results["ssl_days_left"] = (ssl_expiry - datetime.now()).days
            else:
                results["ssl_expiry_date"] = "Could not retrieve"
                results["ssl_days_left"] = 0

            # Broken links
            try:
                broken_links = check_broken_links(url, max_links=20, timeout=5)
                results["broken_links_count"] = len(broken_links)
                save_broken_links(broken_links)
            except Exception as e:
                log_error(f"Broken links check failed: {e}")
                results["broken_links_count"] = 0
            
            # Mobile friendly
            mobile_result = check_mobile_friendly(url, timeout=10)
            results["mobile_friendly"] = "Yes" if mobile_result["is_mobile_friendly"] else "No"
            results["mobile_issues"] = mobile_result.get("issues", [])

            # Screenshot
            try:
                static_folder = os.path.join(os.getcwd(), "static")
                if not os.path.exists(static_folder):
                    os.makedirs(static_folder)

                # ...existing code...
                domain_safe = hostname.replace(".", "_")
                # Ensure screenshot is taken from homepage/root domain
                parsed = urlparse(url)
                root_url = f"{parsed.scheme}://{parsed.netloc}"
                screenshot_file = f"screenshot_{domain_safe}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                screenshot_rel_path = take_screenshot(root_url, screenshot_file)
                results["screenshot"] = screenshot_rel_path
                # ...existing code...
            except Exception as e:
                log_error(f"Screenshot failed: {e}")
                results["screenshot"] = None
 

            # Calculate score and add to results
            results["score"] = calculate_score(
                load_time=results.get("load_time", 5),
                page_size=results.get("page_size_kb", 1000),
                ssl_days=results.get("ssl_days_left", 0),
                broken_count=results.get("broken_links_count", 0),
                was_redirected=results.get("was_redirected", False)
            )

            save_to_csv(results)

            session["results"] = results
            return redirect(url_for("results_page"))

        except Exception as e:
            log_error(f"Error checking {url}: {e}")
            session["error"] = str(e)
            return redirect(url_for("results_page"))

    return render_template("index.html")


@app.route("/results")
def results_page():
    results = session.get("results")
    error = session.get("error")

    session.pop("results", None)
    session.pop("error", None)

    return render_template("results.html", results=results, error=error)


if __name__ == "__main__":
    app.run(debug=True)