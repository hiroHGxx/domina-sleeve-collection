
import json
import requests
import time

def check_and_update_images():
    """
    Reads sleeves.json, checks for specific image URL patterns for IDs >= 41,
    and updates the JSON file if an image is found.
    """
    json_filename = 'sleeves.json'

    try:
        with open(json_filename, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_filename} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_filename}.")
        return

    # URL patterns to check, per user's new request
    url_patterns = [
        "https://www.dominagames.com/wp-content/uploads/2023/09/sleeve{}p.webp"
    ]

    updated_count = 0
    for product in products:
        product_id = product.get('id')
        # Only check for IDs >= 88 and if the image_url is currently empty
        if product_id and product_id >= 88 and product.get('image_url') == "":
            for pattern in url_patterns:
                url_to_check = pattern.format(product_id)
                try:
                    # Use a HEAD request for efficiency, to not download the whole image
                    response = requests.head(url_to_check, timeout=5)
                    if response.status_code == 200:
                        print(f"  [ID {product_id}] Found image at: {url_to_check}")
                        product['image_url'] = url_to_check
                        updated_count += 1
                        # Found the image, no need to check other patterns for this ID
                        break 
                except requests.RequestException:
                    # Ignore connection errors, timeouts, etc.
                    pass
            # Be a good web citizen
            time.sleep(0.2)

    if updated_count > 0:
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"\nUpdate complete. Found and updated {updated_count} image URLs in {json_filename}.")
    else:
        print("\nUpdate complete. No new image URLs were found with the specified patterns.")

if __name__ == "__main__":
    check_and_update_images()
