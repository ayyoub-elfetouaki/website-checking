import csv
import os

def save_to_csv(result, filename="output.csv"):
    file_exists = os.path.isfile(filename)

    try:
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow(['url', 'status_code', 'status_message', 'load_time', 'performance','ssl_expiry', 'ssl_days_left'
                                'page_size_kb', 'content_type', 'server', 'content_encoding', 'cache_control','was_redirected', 'redirect_status_code', 'redirect_target'])
                                

            writer.writerow([
                result['url'],
                result['status_code'],
                result['status_message'],
                f"{result['load_time']} s",       
                result['performance'],
                result.get('ssl_expiry', 'N/A'),
                f"{result.get('ssl_days_left', 'N/A')} days",  
                f"{result.get('page_size_kb', 'N/A')} KB",
                result.get('content_type', 'N/A'),
                result.get('server', 'N/A'),
                result.get('content_encoding', 'N/A'),
                result.get('cache_control', 'N/A'),
                result.get('was_redirected'),
                result.get('redirect_status_code'),
                result.get('redirect_target')])

    except Exception as e:
        print("❌ Failed to save data to CSV.")
        print("Details:", e)

def save_broken_links(broken_links, filename="broken_links.csv"):
    try:
        file_exists = os.path.isfile(filename)

        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Broken Link", "Status"])

            for link, status in broken_links:
                writer.writerow([link, status])

        print("✅ Broken links saved to CSV successfully!")

    except Exception as e:
        print("❌ Failed to save broken links to CSV.")
        print("Details:", e)




