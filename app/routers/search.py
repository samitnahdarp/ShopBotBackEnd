from fastapi import APIRouter, Depends
from app.core.models import Search
from app.database import get_db_connection
from app.workers.hukut_scraper import hukut_scraper
from app.workers.pcmodnepal_scraper import pcmodnepal_scraper
from app.workers.qualitycomputer_scraper import qualitycomputer_scraper
import asyncio

router = APIRouter(prefix="/search", tags=["search"])

_product_id=0
_lock=asyncio.Lock()
@router.post("")
async def search_items(request: Search, conn=Depends(get_db_connection)):
    product=request.product_search
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO app.product_search (searched_product_name) VALUES (%s)",
            (product,)
        )
        conn.commit()
        cursor.execute("""
            SELECT product_search_id
            FROM app.product_search
            ORDER BY created_at DESC
            LIMIT 1;
        """)
        global _product_id
        async with _lock:
            _product_id=cursor.fetchone()[0]

    async with asyncio.TaskGroup() as tg:

        hukut_task = tg.create_task(
            hukut_scraper(product)
        )

        pcmodnepal_task = tg.create_task(
            pcmodnepal_scraper(product)
        )

        qualitycomputer_task = tg.create_task(
            qualitycomputer_scraper(product)
        )

    hukut_data = hukut_task.result()
    pcmodnepal_data = pcmodnepal_task.result()
    qualitycomputer_data = qualitycomputer_task.result()

    commit_data(hukut_data,conn=conn)
    commit_data(pcmodnepal_data,conn=conn)
    commit_data(qualitycomputer_data,conn=conn)
    data=None
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT row_to_json(p)
            FROM (
                SELECT
                    name,
                    rating,
                    price,
                    description,
                    link,
                    image
                FROM app.scraped_product
                WHERE product_search_id = %s
            ) p;
            """,(_product_id,)
        )
        data=cursor.fetchall()
        conn.commit()

    return {
        "status": "executed",
        "_product_id": _product_id,
        "products": data
    }


def commit_data(json_data,conn):
    query = """
    INSERT INTO app.scraped_product (
        product_search_id,
        name,
        rating,
        price,
        description,
        link,
        image
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """;
    if(json_data==None):
        return None;
    with conn.cursor() as cur:
        for p in json_data:
            cur.execute(query, (
                _product_id,
                p.name,
                p.rating,
                p.price,
                p.description,
                p.link,
                p.image
            ))
    conn.commit()