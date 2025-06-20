# Shopify Scraper - Complete Guide

## About

This enhanced Shopify scraper extracts comprehensive product information from Shopify stores, including detailed product data that's not available through the standard Shopify API. It goes beyond basic product information to capture:

- **Basic Product Data**: Title, price, SKU, variants, stock status
- **Detailed Information**: Product descriptions, key features, usage instructions
- **Ingredients**: Both individual ingredient details and complete ingredient lists
- **Images**: Product and variant-specific images
- **Rich Content**: Information from accordion sections and expandable content areas

The scraper writes data incrementally to CSV format, ensuring you don't lose progress if the script is interrupted.

## What Makes This Scraper Special

Unlike basic Shopify scrapers that only use the products.json API, this tool:
- ✅ **Scrapes actual product pages** to get detailed accordion content
- ✅ **Extracts ingredient information** with descriptions and benefits
- ✅ **Handles multiple HTML layouts** with robust parsing
- ✅ **Writes data immediately** to prevent data loss
- ✅ **Respects rate limits** with built-in delays
- ✅ **Provides real-time progress** updates

## Prerequisites

- Python 3.6 or higher
- No additional libraries required (uses built-in modules)

## How to Find Collections (Categories)

### Method 1: List All Collections
First, discover what collections are available on the Shopify store:

```bash
python shopify-full.py --list-collections https://store-url.com
```

**Example:**
```bash
python shopify-full.py --list-collections https://cantabrialabs.co.uk/
```

This will output all collection handles like:
```
heliocare
endocare
neoretin
biretix
frontpage
```

### Method 2: Manual Discovery
You can also find collections by browsing the website:

1. **Visit the store's website**
2. **Look for navigation menus** - collections often appear as main menu items
3. **Check category/collection pages** - URLs usually look like: `https://store.com/collections/collection-name`
4. **The collection handle** is the part after `/collections/` in the URL

**Example URLs:**
- `https://cantabrialabs.co.uk/collections/heliocare` → handle: `heliocare`
- `https://store.com/collections/skincare-products` → handle: `skincare-products`

## How to Run the Scraper

### Basic Usage

**Scrape ALL products from ALL collections:**
```bash
python shopify-full.py https://store-url.com
```

**Scrape specific collection(s):**
```bash
python shopify-full.py -c collection-name https://store-url.com
```

**Scrape multiple collections:**
```bash
python shopify-full.py -c collection1,collection2,collection3 https://store-url.com
```

### Real Examples

**1. Scrape only HELIOCARE products:**
```bash
python shopify-full.py -c heliocare https://cantabrialabs.co.uk/
```

**2. Scrape HELIOCARE and ENDOCARE products:**
```bash
python shopify-full.py -c heliocare,endocare https://cantabrialabs.co.uk/
```

**3. Scrape all products from the store:**
```bash
python shopify-full.py https://cantabrialabs.co.uk/
```

**4. List available collections first:**
```bash
python shopify-full.py --list-collections https://cantabrialabs.co.uk/
```

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--list-collections` | Show all available collections | `--list-collections` |
| `-c` or `--collections` | Specify collections to scrape (comma-separated) | `-c heliocare,endocare` |

## Output

The scraper creates a file called `products.csv` with the following columns:

| Column | Description |
|--------|-------------|
| Code | Product SKU/code |
| Collection | Collection name the product belongs to |
| Category | Product type/category |
| Name | Product title |
| Variant Name | Product variant (size, color, etc.) |
| Price | Product price |
| In Stock | Stock availability (Yes/No) |
| URL | Direct link to product page |
| Image URL | Product image URL |
| Body | Main product description |
| Key Information | Bullet points from "Key Information" section |
| How to Use | Usage instructions and precautions |
| Key Ingredients | JSON array of ingredient details with descriptions |
| All Ingredients | Complete ingredients list |

## Progress Monitoring

The scraper provides real-time feedback:

```
Processing collection: HELIOCARE Products (heliocare)
Scraping detailed info for: HELIOCARE 360° Advanced Gel Body SPF50+
  - Found 3 key ingredients
  - Found full ingredients list
Scraping detailed info for: HELIOCARE Oral Capsules
  - Found 1 key ingredients
  - Found full ingredients list
```

You can also monitor the CSV file as it's being written - it updates in real-time!

## Important Notes

### Rate Limiting
- The scraper includes **1-second delays** between product page requests
- If blocked, it will **automatically sleep for 3 minutes** and retry
- This ensures you don't get banned from the website

### Data Integrity
- Data is **written immediately** to CSV (not stored in memory)
- If the script crashes, **you won't lose scraped data**
- You can manually resume by checking what's already in the CSV

### Respectful Scraping
- Only scrapes **publicly available information**
- Uses **realistic delays** between requests
- Identifies itself with a **standard browser user agent**

## Troubleshooting

### Common Issues

**1. "Invalid URL" error:**
- Make sure the URL includes `https://` or `http://`
- Remove trailing slashes from URLs

**2. "Collection not found":**
- Use `--list-collections` to see available collections
- Check spelling of collection handles

**3. "Blocked" messages:**
- This is normal - the script will automatically retry
- Wait for the 3-minute sleep to complete

**4. Missing ingredient data:**
- Some products may not have detailed ingredient information
- The scraper will still capture basic product data

### Performance Tips

- **Start with specific collections** using `-c` rather than scraping everything
- **Monitor the CSV file** to track progress
- **Let the script run uninterrupted** for best results

## Example Workflow

1. **Discover collections:**
   ```bash
   python shopify-full.py --list-collections https://cantabrialabs.co.uk/
   ```

2. **Test with one collection:**
   ```bash
   python shopify-full.py -c heliocare https://cantabrialabs.co.uk/
   ```

3. **Review the output CSV** to ensure data quality

4. **Scale up to multiple collections** if needed:
   ```bash
   python shopify-full.py -c heliocare,endocare,neoretin https://cantabrialabs.co.uk/
   ```

## Legal and Ethical Considerations

- Only scrape **publicly available information**
- Respect the website's **robots.txt** file
- Don't overload servers with **too many rapid requests**
- Use scraped data **responsibly** and in compliance with terms of service
- Consider **reaching out to the website owner** for permission if scraping large amounts of data

---

Happy scraping! 🚀