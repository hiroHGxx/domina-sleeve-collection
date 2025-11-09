import json
import requests
import time
import re

def validate_image_urls():
    """
    Reads sleeves.json and validates each image_url.
    Checks:
    1. If the URL is not empty.
    2. If the URL is live and returns a 200 status code.
    3. If the URL filename contains the product ID.
    """
    json_filename = 'sleeves.json'
    issues = []

    try:
        with open(json_filename, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_filename} not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from {json_filename}. Invalid character at {e.pos}.")
        return

    print("Starting URL validation...")
    for i, product in enumerate(products):
        product_id = product.get('id')
        image_url = product.get('image_url')
        
        print(f"  Checking ID {product_id}...")

        # 1. Check if URL is empty
        if not image_url:
            issues.append(f"[ID {product_id}] - URL is empty.")
            continue

        # 2. Check if URL is live
        try:
            response = requests.head(image_url, timeout=10)
            if response.status_code != 200:
                issues.append(f"[ID {product_id}] - URL returned status {response.status_code}: {image_url}")
        except requests.RequestException as e:
            issues.append(f"[ID {product_id}] - URL failed to connect: {e}")
            continue # If we can't connect, no point in other checks

        # 3. Check if filename contains the ID
        # This is a heuristic and might have false positives, but it's a good sanity check
        if str(product_id) not in image_url:
             # To avoid false alarms for irregular names like MiS02_ローランド.jpg,
             # let's only flag if the filename looks like a standard "sleeve" name
             if 'sleeve' in image_url.lower():
                issues.append(f"[ID {product_id}] - URL may be incorrect. Filename does not contain the ID '{product_id}': {image_url}")

        time.sleep(0.2) # Be a good web citizen

    print("\n--- Validation Report ---")
    if not issues:
        print("✅ All image URLs appear to be valid and correct!")
    else:
        print(f"Found {len(issues)} potential issue(s):")
        for issue in issues:
            print(f"- {issue}")
    print("-------------------------\\n")


if __name__ == "__main__":
    validate_image_urls()
