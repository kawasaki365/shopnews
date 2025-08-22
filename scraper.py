import json
import requests
from bs4 import BeautifulSoup


def fetch_ssense():
    url = 'https://www.ssense.com/en-jp/men/sale/needles/pants'
    products = []
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text, 'html.parser')
        for card in soup.select('div.product-card'):
            title_tag = card.select_one('[data-qa="product-name"]')
            title = title_tag.get_text(strip=True) if title_tag else ''
            if 'Track' not in title and 'track' not in title:
                continue
            link_tag = card.find('a', href=True)
            link = 'https://www.ssense.com' + link_tag['href'] if link_tag else url
            price_tag = card.select_one('.price')
            price = price_tag.get_text(strip=True) if price_tag else ''
            img_tag = card.find('img')
            image = img_tag['src'] if img_tag else ''
            products.append({
                'title': title,
                'url': link,
                'price': price,
                'image': image
            })
    except Exception as e:
        print('Error parsing SSENSE:', e)
    return products


def fetch_end():
    url = 'https://www.endclothing.com/jp/sale?brand=needles'
    products = []
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text, 'html.parser')
        for card in soup.select('div.product-grid-item'):
            title_tag = card.select_one('.product-card__name') or card.select_one('.product-name')
            title = title_tag.get_text(strip=True) if title_tag else ''
            if 'Track' not in title and 'track' not in title:
                continue
            link_tag = card.find('a', href=True)
            link = link_tag['href'] if link_tag else ''
            price_tag = card.select_one('.product-price') or card.select_one('.price')
            price = price_tag.get_text(strip=True) if price_tag else ''
            img_tag = card.find('img')
            image = img_tag['src'] if img_tag else ''
            products.append({
                'title': title,
                'url': link,
                'price': price,
                'image': image
            })
    except Exception as e:
        print('Error parsing END Clothing:', e)
    return products


def fetch_nepenthes():
    """Fetch Needles track pants from Nepenthes online store."""
    url = 'https://onlinestore.nepenthes.co.jp/collections/needles-pant/products.json'
    products = []
    try:
        resp = requests.get(url)
        data = resp.json()
        for prod in data.get('products', []):
            title = prod.get('title', '')
            # Only include items with 'Track' in the title
            if 'TRACK' not in title.upper():
                continue
            handle = prod.get('handle', '')
            product_url = f"https://onlinestore.nepenthes.co.jp/products/{handle}"
            # Price is in yen as string; convert to integer and format
            variant = prod.get('variants', [{}])[0]
            price_str = variant.get('price', '')
            try:
                price_int = int(price_str)
                price = f"\u00a5{price_int:,}"
            except Exception:
                price = price_str
            images = prod.get('images', [])
            image = images[0].get('src', '') if images else ''
            published_at = prod.get('published_at', '')
            products.append({
                'title': title,
                'url': product_url,
                'price': price,
                'image': image,
                'published_at': published_at
            })
    except Exception:
        # If any error occurs, return current products
        pass
    return products


def fetch_daytona():
    """Placeholder for Daytona Park scraping. Currently returns empty list."""
    return []


def fetch_parco():
    """Placeholder for online.parco.jp scraping. Currently returns empty list."""
    return []


def main():
    all_products = []
    # Gather products from all sources
    all_products += fetch_ssense()
    all_products += fetch_end()
    all_products += fetch_nepenthes()
    all_products += fetch_daytona()
    all_products += fetch_parco()
    # Deduplicate by URL
    seen = set()
    unique_products = []
    for item in all_products:
        url_key = item.get('url', '')
        if url_key and url_key not in seen:
            seen.add(url_key)
            unique_products.append(item)
    # Sort by published_at descending (empty strings will sort last)
    unique_products.sort(key=lambda x: x.get('published_at', ''), reverse=True)
    # Limit to top 10 newest
    top_products = unique_products[:10]
    # Ensure docs directory exists
    import os
    os.makedirs('docs', exist_ok=True)
    # Write to docs/data.json
    with open('docs/data.json', 'w', encoding='utf-8') as f:
        json.dump(top_products, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
