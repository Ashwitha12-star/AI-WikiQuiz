import requests
from bs4 import BeautifulSoup

def scrape_wikipedia_content(url: str):
    """
    Scrapes Wikipedia article content and returns (title, text_content).
    Only uses raw HTML scraping (no Wikipedia API).
    """
    try:
        print(f"🕵️‍♀️ Scraping Wikipedia URL: {url}")

        # Validate URL
        if not url.startswith("http"):
            url = "https://en.wikipedia.org/wiki/" + url.replace(" ", "_")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"⚠️ Failed to fetch Wikipedia page. Status: {response.status_code}")
            return None, None

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title
        title = soup.find("h1", {"id": "firstHeading"})
        title_text = title.get_text(strip=True) if title else "Untitled Article"

        # Extract main content
        content_div = soup.find("div", {"id": "mw-content-text"})
        paragraphs = content_div.find_all("p", recursive=True) if content_div else []

        text_content = " ".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

        # Clean up whitespace
        text_content = text_content.replace("\n", " ").strip()

        if not text_content:
            print("⚠️ No valid text found in article content.")
            return title_text, None

        print(f"✅ Successfully scraped article: {title_text[:50]}...")
        return title_text, text_content

    except Exception as e:
        print(f"❌ Error scraping Wikipedia page: {e}")
        return None, None
