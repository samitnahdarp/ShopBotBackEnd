"""
robots.txt for https://hukut.com

User-Agent: *
Allow: /
Disallow: /dashboard
Disallow: /cart

Host: https://hukut.com
Sitemap: https://hukut.com/sitemap.xml
"""

"""
for sorting by price in ascending order, use:
"sort": [{ "price": 1 }]
for sorting by price in descending order, use:
"sort": [{ "price": -1 }]
for sorting by relevance, use:
"sort": [{ "relevance": 0 }]
for sorting by rating in descending order, use:
"sort": [{ "rating": -1 }]
"""

import aiohttp
import asyncio
import time
import random
from app.core.models import Product
from typing import Optional, Union, List

_last_request = 0
_lock = asyncio.Lock()

async def hukut_scraper(Product: str) -> Optional[Union[Product, List[Product]]] :
    global _last_request
    async with _lock:
        now = time.monotonic()
        delay = 2 + abs(random.random()) - (now - _last_request)

        if delay > 0:
            await asyncio.sleep(delay)

        _last_request = time.monotonic()

    async with aiohttp.ClientSession() as session:
        url = "https://hukut.com/api-server/v1/Product/list-elastic"

        payload = {
            "searchText": Product,
            "pagination": {"limit": 20, "offset": 0},
            "sort": [{"relevance": 0}]
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        async with session.post(url, json=payload, headers=headers) as response:
            data = await response.json()
            return get_hukut_Products(data)

def get_hukut_Products(data: dict,) -> Optional[Union[Product, List[Product]]]:
    Products: List[Product] = []

    for item in data.get("data", {}).get("rows", []):
        name = item.get("name") or ""

        rating = item.get("averageRating") or 0

        default_variant = item.get("defaultVariant") or {}
        price = default_variant.get("price") or 0

        slug = item.get("slug") or ""
        link = f"https://hukut.com/{slug}" if slug else ""

        image = item.get("image", {}).get("cdn") or ""

        description = name  # no separate description field in source

        Products.append(
            Product(
                name=name,
                rating=float(rating),
                price=float(price),
                link=link,
                image=image,
                description=description,
            )
        )

    if not Products:
        return None
    if len(Products) == 1:
        return Products[0]
    return Products