import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def check_broken_links(base_url, max_links=20, timeout=5):
    broken_links = []
    try:
        response = requests.get(base_url, timeout=timeout)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')[:max_links]  # Limit to first N links

        for link in links:
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                try:
                    res = requests.head(full_url, allow_redirects=True, timeout=timeout)
                    if res.status_code >= 400:
                        broken_links.append((full_url, res.status_code))
                except requests.RequestException:
                    broken_links.append((full_url, "Request Failed"))

    except Exception as e:
        print("Error fetching page for broken links:", e)

    return broken_links

