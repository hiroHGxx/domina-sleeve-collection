
import sys
import requests
from bs4 import BeautifulSoup

def get_image_url(sleeve_id):
    """
    Scrapes a single sleeve product page specifically for the main image URL.
    Prints the absolute URL if found, otherwise prints "N/A".
    """
    url = f"https://www.dominagames.com/sleeves{sleeve_id}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print("N/A")
            return
    except requests.RequestException:
        print("N/A")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # First, try the specific selector for the main item photo
    image_tag = soup.select_one('#item_photo img')
    
    # If the first selector fails, try a more generic one for WordPress post images
    if not image_tag:
        image_tag = soup.select_one('.wp-post-image')

    if image_tag and image_tag.has_attr('src'):
        image_url = image_tag['src']
        # Ensure the URL is absolute
        if not image_url.startswith('http'):
            # Assuming it's a relative path from the root
            base_url = "https://www.dominagames.com"
            if image_url.startswith('/'):
                image_url = base_url + image_url
            else:
                image_url = base_url + '/' + image_url
        print(image_url)
    else:
        print("N/A")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_image_url.py <sleeve_id>")
        sys.exit(1)
    
    sleeve_id_arg = sys.argv[1]
    if not sleeve_id_arg.isdigit():
        print("Error: <sleeve_id> must be a number.")
        sys.exit(1)
        
    get_image_url(sleeve_id_arg)
