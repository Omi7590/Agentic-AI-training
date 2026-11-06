# RTI Mitra - fetch.py
# Downloads 3+ RTI source documents from the web into data/raw/
# Uses requests with timeouts and full error handling.

import os
import requests

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "data", "raw")

# Documents to download: (filename, url)
DOCUMENTS = [
    (
        "rti_act_2005.pdf",
        "https://rti.gov.in/Writereaddata/RTI-Act.pdf"
    ),
    (
        "rti_home_page.html",
        "https://rti.gov.in/"
    ),
    (
        "rtionline_portal.html",
        "https://rtionline.gov.in/"
    ),
]

def download(filename, url):
    """Download one document and save it to data/raw/. Returns True on success."""
    dest = os.path.join(RAW_DIR, filename)
    print(f"[FETCH] {url}")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        with open(dest, "wb") as f:
            f.write(response.content)
        size_kb = len(response.content) // 1024
        print(f"[OK]    Saved {filename} ({size_kb} KB)")
        return True
    except requests.exceptions.Timeout:
        print(f"[ERROR] Timeout fetching {url}")
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP error for {url}: {e}")
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Connection failed for {url}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Unexpected error for {url}: {e}")
    return False

def fetch_all():
    os.makedirs(RAW_DIR, exist_ok=True)
    success = 0
    for filename, url in DOCUMENTS:
        if download(filename, url):
            success += 1
    print(f"\n[DONE] Downloaded {success}/{len(DOCUMENTS)} documents to data/raw/")

if __name__ == "__main__":
    fetch_all()
