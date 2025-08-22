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


def main():
    all_products = []
    all_products += fetch_ssense()
    all_products += fetch_end()
    # deduplicate by url
    seen = set()
    unique_products = []
    for item in all_products:
        if item.get('url') and item['url'] not in seen:
            seen.add(item['url'])
            unique_products.append(item)
    # ensure docs directory exists
    import os
    os.makedirs('docs', exist_ok=True)
    # write to docs/data.json
    with open('docs/data.json', 'w', encoding='utf-8') as f:
        json.dump(unique_products, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
