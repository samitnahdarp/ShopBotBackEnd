""" 
robots.txt for pcmodnepal.com

User-agent: *
Disallow: /wp-content/uploads/wc-logs/
Disallow: /wp-content/uploads/woocommerce_transient_files/
Disallow: /wp-content/uploads/woocommerce_uploads/
Disallow: /*?add-to-cart=
Disallow: /*?*add-to-cart=
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php

# START YOAST BLOCK
# ---------------------------
User-agent: *
Disallow:

Sitemap: https://pcmodnepal.com/sitemap_index.xml
# ---------------------------
# END YOAST BLOCK
"""

from enum import Enum
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import time
import random
from app.make_request import send_request
from app.core.models import Product
from typing import Optional, Union, List
import re


class OrderBy(Enum):
    popularity = "popularity"
    rating = "rating"
    price_asc = "price"
    price_desc = "price-desc"
    relevance = "relevance"

_last_request = 0
_lock = asyncio.Lock()

async def pcmodnepal_scraper(Product: str) -> Optional[Union[Product,List[Product]]]:
    global _last_request
    async with _lock:
        now = time.monotonic()
        delay = 2 + abs(random.random()) - (now - _last_request)
        if delay > 0:
            await asyncio.sleep(delay)
        _last_request = time.monotonic()
    
    page_number = 1
    url=f"https://pcmodnepal.com/shop/page/{page_number}/"
    params={
        "orderby": OrderBy.relevance.value,
        "shop_view": "list",
        "s": Product,
        "post_type": "Product",
        "per_page": "24"
    }
    html_file=await send_request(url=url, method="GET", params=params)
    with open("pcmodnepal.html",'w',encoding="utf-8") as f:
        f.write(str(html_file))
    return pcmodnepal_parser(html_content=html_file)
        
def pcmodnepal_parser(html_content: str) -> Optional[Union[Product, List[Product]]]:
    soup = BeautifulSoup(html_content, "html.parser")
    products: List[Product] = []

    # WooCommerce / Woodmart theme product item containers
    product_elements = soup.find_all(class_=lambda x: x and ("product-grid-item" in x or "type-product" in x))

    base_url = "https://pcmodnepal.com"

    for item in product_elements:
        # Name
        name_el = item.find(class_="wd-entities-title") or item.find("h3", class_="product-title")
        name = name_el.get_text(strip=True) if name_el else "Unknown Product"

        # Link
        link_el = name_el.find("a") if name_el else item.find("a", class_="product-image-link")
        href = link_el.get("href") if link_el else ""
        link = f"{base_url}{href}" if href.startswith("/") else href

        # Price
        price_el = item.find("span", class_="woocommerce-Price-amount")
        raw_price = ""
        if price_el:
            raw_price = re.sub(r"[^\d.]", "", price_el.get_text(strip=True))

        try:
            price = float(raw_price) if raw_price else 0.0
        except ValueError:
            price = 0.0

        # Image
        img_el = item.find("img")
        img_src = ""
        if img_el:
            img_src = img_el.get("data-lazy-src") or img_el.get("data-src") or img_el.get("src") or ""

        image = f"{base_url}{img_src}" if img_src.startswith("/") else img_src
        rating = 0.0
        description = name

        products.append(
            Product(
                name=name,
                rating=float(rating),
                price=price,
                link=link,
                image=image,
                description=description,
            )
        )

    if not products:
        return None
    if len(products) == 1:
        return products[0]
    return products