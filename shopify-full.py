import sys
import csv
import json
import time
import urllib.request
from urllib.error import HTTPError
from optparse import OptionParser
import re
from html import unescape
from urllib.parse import urljoin

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'

def get_page(url, page, collection_handle=None):
    full_url = url
    if collection_handle:
        full_url += '/collections/{}'.format(collection_handle)
    full_url += '/products.json'
    req = urllib.request.Request(
        full_url + '?page={}'.format(page),
        data=None,
        headers={
            'User-Agent': USER_AGENT
        }
    )
    while True:
        try:
            data = urllib.request.urlopen(req).read()
            break
        except HTTPError:
            print('Blocked! Sleeping...')
            time.sleep(180)
            print('Retrying')
        
    products = json.loads(data.decode())['products']
    return products

def get_product_page_html(product_url):
    """Fetch the HTML content of a product page"""
    req = urllib.request.Request(
        product_url,
        data=None,
        headers={
            'User-Agent': USER_AGENT
        }
    )
    
    try:
        response = urllib.request.urlopen(req)
        html_content = response.read().decode('utf-8')
        return html_content
    except Exception as e:
        print(f"Error fetching {product_url}: {e}")
        return None

def clean_html_text(html_text):
    """Remove HTML tags and clean up text"""
    if not html_text:
        return ""
    
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', html_text)
    # Decode HTML entities
    clean_text = unescape(clean_text)
    # Remove extra whitespace and normalize
    clean_text = ' '.join(clean_text.split())
    # Remove problematic Unicode characters
    clean_text = clean_text.replace('\u200b', '')  # zero-width space
    clean_text = clean_text.replace('\u200c', '')  # zero-width non-joiner
    clean_text = clean_text.replace('\u200d', '')  # zero-width joiner
    return clean_text.strip()

def extract_accordion_content(html_content):
    """Extract content from accordion sections with improved robustness"""
    accordion_data = {}
    
    if not html_content:
        return accordion_data
    
    # More flexible pattern for Key Information
    key_info_patterns = [
        r'<summary[^>]*>.*?Key information.*?</summary>\s*<div[^>]*class="accordion__content[^"]*"[^>]*>(.*?)</div>',
        r'Key information.*?</h2>.*?</summary>\s*<div[^>]*>(.*?)</div>\s*</details>',
        r'Key information.*?</summary>\s*<div[^>]*>(.*?)</div>'
    ]
    
    for pattern in key_info_patterns:
        key_info_match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        if key_info_match:
            accordion_data['key_information'] = clean_html_text(key_info_match.group(1))
            break
    
    # More flexible pattern for How to use
    how_to_use_patterns = [
        r'<summary[^>]*>.*?How to use.*?</summary>\s*<div[^>]*class="accordion__content[^"]*"[^>]*>(.*?)</div>',
        r'How to use.*?</h2>.*?</summary>\s*<div[^>]*>(.*?)</div>\s*</details>',
        r'How to use.*?</summary>\s*<div[^>]*>(.*?)</div>'
    ]
    
    for pattern in how_to_use_patterns:
        how_to_use_match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        if how_to_use_match:
            accordion_data['how_to_use'] = clean_html_text(how_to_use_match.group(1))
            break
    
    # Extract Ingredients section - more robust approach
    ingredients_patterns = [
        r'<summary[^>]*>.*?Ingredients.*?</summary>\s*<div[^>]*>(.*?)</details>',
        r'Ingredients.*?</h2>.*?</summary>\s*<div[^>]*>(.*?)</details>',
        r'Ingredients.*?</summary>\s*<div[^>]*>(.*?)(?=<a href=|$)'
    ]
    
    ingredients_content = None
    for pattern in ingredients_patterns:
        ingredients_match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        if ingredients_match:
            ingredients_content = ingredients_match.group(1)
            break
    
    if ingredients_content:
        # Extract key ingredients with more flexible patterns
        key_ingredients = []
        
        # Try multiple patterns for ingredient cards
        ingredient_card_patterns = [
            r'<div class="ingredient-card"[^>]*>(.*?)(?=<div class="ingredient-card"|</div>\s*<div class="twcss-text-black|$)',
            r'<div class="ingredient-card">(.*?)(?=</div>\s*</div>)',
            r'<h2 class="ingredient-card__title[^"]*"[^>]*>(.*?)</h2>(.*?)(?=<h2 class="ingredient-card__title|<div class="twcss-text-black|$)'
        ]
        
        for card_pattern in ingredient_card_patterns:
            ingredient_cards = re.findall(card_pattern, ingredients_content, re.DOTALL)
            if ingredient_cards:
                break
        
        # If we found cards, process them
        if ingredient_cards:
            for card in ingredient_cards:
                if isinstance(card, tuple):
                    # Handle tuple results from some patterns
                    card_content = ''.join(card)
                else:
                    card_content = card
                
                # Extract ingredient name
                name_patterns = [
                    r'<h2[^>]*class="ingredient-card__title[^"]*"[^>]*>(.*?)</h2>',
                    r'<h2[^>]*>(.*?)</h2>'
                ]
                
                ingredient_name = ""
                for name_pattern in name_patterns:
                    name_match = re.search(name_pattern, card_content, re.DOTALL)
                    if name_match:
                        ingredient_name = clean_html_text(name_match.group(1))
                        break
                
                if ingredient_name:  # Only process if we found a name
                    # Extract description
                    desc_patterns = [
                        r'<div class="ingredient-card__description"[^>]*>(.*?)</div>',
                        r'ingredient-card__description[^>]*>(.*?)(?=<div class="ingredients-card__benefits"|</div>)'
                    ]
                    
                    description = ""
                    for desc_pattern in desc_patterns:
                        desc_match = re.search(desc_pattern, card_content, re.DOTALL)
                        if desc_match:
                            description = clean_html_text(desc_match.group(1))
                            break
                    
                    # Extract benefits
                    benefits_patterns = [
                        r'<div class="ingredients-card__benefits">.*?<div[^>]*>(.*?)</div>',
                        r'Benefits:.*?<div[^>]*>(.*?)</div>',
                        r'Benefits:</h4>.*?<p>(.*?)</p>'
                    ]
                    
                    benefits = ""
                    for benefits_pattern in benefits_patterns:
                        benefits_match = re.search(benefits_pattern, card_content, re.DOTALL)
                        if benefits_match:
                            benefits = clean_html_text(benefits_match.group(1))
                            break
                    
                    key_ingredients.append({
                        'name': ingredient_name,
                        'description': description,
                        'benefits': benefits
                    })
        
        # Extract full ingredients list with multiple patterns
        all_ingredients_patterns = [
            r'All ingredients.*?<p><span[^>]*>(.*?)</span></p>',
            r'All ingredients.*?<span[^>]*>(.*?)</span>',
            r'All ingredients.*?<p>(.*?)</p>',
            r'<div class="twcss-text-black twcss-font-bold twcss-py-4">All ingredients</div>\s*<p[^>]*>(.*?)</p>'
        ]
        
        all_ingredients = ""
        for pattern in all_ingredients_patterns:
            all_ingredients_match = re.search(pattern, ingredients_content, re.DOTALL | re.IGNORECASE)
            if all_ingredients_match:
                all_ingredients = clean_html_text(all_ingredients_match.group(1))
                break
        
        accordion_data['key_ingredients'] = key_ingredients
        accordion_data['all_ingredients'] = all_ingredients
    
    return accordion_data

def get_page_collections(url):
    full_url = url + '/collections.json'
    page = 1
    while True:
        req = urllib.request.Request(
            full_url + '?page={}'.format(page),
            data=None,
            headers={
                'User-Agent': USER_AGENT
            }
        )
        while True:
            try:
                data = urllib.request.urlopen(req).read()
                break
            except HTTPError:
                print('Blocked! Sleeping...')
                time.sleep(180)
                print('Retrying')

        cols = json.loads(data.decode())['collections']
        if not cols:
            break
        for col in cols:
            yield col
        page += 1

def check_shopify(url):
    try:
        get_page(url, 1)
        return True
    except Exception:
        return False

def fix_url(url):
    fixed_url = url.strip()
    if not fixed_url.startswith('http://') and \
       not fixed_url.startswith('https://'):
        fixed_url = 'https://' + fixed_url

    return fixed_url.rstrip('/')

def extract_products_collection(url, col, csv_writer, csv_file, seen_variants):
    """Extract products and write to CSV immediately"""
    page = 1
    products = get_page(url, page, col['handle'])
    while products:
        for product in products:
            title = product['title']
            product_type = product['product_type']
            product_url = url + '/products/' + product['handle']
            product_handle = product['handle']
            
            print(f"Scraping detailed info for: {title}")
            
            # Get detailed product information from the product page
            html_content = get_product_page_html(product_url)
            accordion_data = extract_accordion_content(html_content)
            
            # Debug output for ingredients
            if accordion_data.get('key_ingredients'):
                print(f"  - Found {len(accordion_data['key_ingredients'])} key ingredients")
            else:
                print(f"  - No key ingredients found")
            
            if accordion_data.get('all_ingredients'):
                print(f"  - Found full ingredients list")
            else:
                print(f"  - No full ingredients list found")

            def get_image(variant_id):
                images = product['images']
                for i in images:
                    k = [str(v) for v in i['variant_ids']]
                    if str(variant_id) in k:
                        return i['src']
                return ''

            for i, variant in enumerate(product['variants']):
                price = variant['price']
                option1_value = variant['option1'] or ''
                option2_value = variant['option2'] or ''
                option3_value = variant['option3'] or ''
                option_value = ' '.join([option1_value, option2_value,
                                         option3_value]).strip()
                sku = variant['sku']
                main_image_src = ''
                if product['images']:
                    main_image_src = product['images'][0]['src']

                image_src = get_image(variant['id']) or main_image_src
                stock = 'Yes'
                if not variant['available']:
                    stock = 'No'

                variant_id = product_handle + str(variant['id'])
                if variant_id in seen_variants:
                    continue

                seen_variants.add(variant_id)
                
                # Write row immediately to CSV
                csv_writer.writerow([
                    sku or '', 
                    str(col['title']),
                    product_type or '',
                    title or '', 
                    option_value or '',
                    price or '',
                    stock or '', 
                    product_url or '',
                    image_src or '', 
                    clean_html_text(str(product['body_html'])) if product.get('body_html') else '',
                    accordion_data.get('key_information', ''),
                    accordion_data.get('how_to_use', ''),
                    json.dumps(accordion_data.get('key_ingredients', [])),
                    accordion_data.get('all_ingredients', '')
                ])
                
                # Flush the file to ensure data is written
                csv_file.flush()
                
            # Add a small delay to be respectful to the server
            time.sleep(1)

        page += 1
        products = get_page(url, page, col['handle'])

def extract_products(url, path, collections=None):
    seen_variants = set()
    
    # Open CSV file and write header immediately
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Code', 'Collection', 'Category',
                         'Name', 'Variant Name', 'Price', 'In Stock', 
                         'URL', 'Image URL', 'Body', 'Key Information',
                         'How to Use', 'Key Ingredients', 'All Ingredients'])
        
        for col in get_page_collections(url):
            if collections and col['handle'] not in collections:
                continue
            
            print(f"\nProcessing collection: {col['title']} ({col['handle']})")
            extract_products_collection(url, col, writer, f, seen_variants)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--list-collections", dest="list_collections",
                      action="store_true",
                      help="List collections in the site")
    parser.add_option("--collections", "-c", dest="collections",
                      default="",
                      help="Download products only from the given collections (comma separated)")
    (options, args) = parser.parse_args()
    if len(args) > 0:
        url = fix_url(args[0])
        if options.list_collections:
            for col in get_page_collections(url):
                print(col['handle'])
        else:
            collections = []
            if options.collections:
                collections = options.collections.split(',')
            extract_products(url, 'products.csv', collections)