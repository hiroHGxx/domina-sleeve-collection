import requests
from bs4 import BeautifulSoup
import json
import re
import time

def scrape_sleeve_page(sleeve_id):
    """Scrapes a single sleeve product page for its details."""
    url = f"https://www.dominagames.com/sleeves{sleeve_id}"
    print(f"Fetching {url}...")

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"  -> Page not found or error (Status: {response.status_code}). Skipping.")
            return None
    except requests.RequestException as e:
        print(f"  -> Request failed: {e}. Skipping.")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # --- Extract Product Name ---
    # Try a few selectors in order of preference, with the page title as a fallback.
    product_name = "N/A"
    product_name_tag = soup.find('div', id='item_name') or soup.find('h1')
    if product_name_tag:
        product_name = product_name_tag.get_text(strip=True)
    elif soup.title:
        # Use the page title as a fallback and clean it up
        product_name = soup.title.string.replace('- Domina Games', '').strip()


    # --- Extract Image URL ---
    # Look for an image within the main item photo div
    image_tag = soup.select_one('#item_photo img')
    image_url = image_tag['src'] if image_tag and image_tag.has_attr('src') else "N/A"
    if image_url != "N/A" and not image_url.startswith('http'):
        image_url = f"https://www.dominagames.com{image_url}"


    # --- Extract Details from Text ---
    details = {}
    page_text = soup.get_text()

    # Price
    price_match = re.search(r'価格\s*[:：]\s*([\d,]+円)', page_text)
    if not price_match: # Fallback for different formats
        price_match = re.search(r'([\d,]+円)\s*（税込）', page_text)
    details['price'] = price_match.group(1) if price_match else "N/A"

    # Quantity
    quantity_match = re.search(r'封入枚数\s*[:：]\s*(\d+枚)', page_text)
    details['quantity'] = quantity_match.group(1) if quantity_match else "N/A"

    # Size
    size_match = re.search(r'サイズ\s*[:：]\s*([0-9]+mm\s*×\s*[0-9]+mm)', page_text)
    details['size'] = size_match.group(1) if size_match else "N/A"
    
    # Release Date
    release_date_match = re.search(r'発売日\s*[:：]\s*(.+)', page_text)
    details['release_date'] = release_date_match.group(1).strip() if release_date_match else "N/A"


    return {
        "id": sleeve_id,
        "url": url,
        "product_name": product_name,
        "image_url": image_url,
        "price": details['price'],
        "quantity": details['quantity'],
        "size": details['size'],
        "release_date": details['release_date']
    }

def main():
    """Main function to scrape all sleeves and save to JSON."""
    all_sleeves_data = []
    # Per user request, search up to 120
    for i in range(1, 121):
        data = scrape_sleeve_page(i)
        if data:
            all_sleeves_data.append(data)
        # Be a good web citizen and pause between requests
        time.sleep(0.5) 

    output_filename = 'sleeves.json'
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(all_sleeves_data, f, ensure_ascii=False, indent=2)

    print(f"\nScraping complete. Data saved to {output_filename}")

if __name__ == "__main__":
    main()
