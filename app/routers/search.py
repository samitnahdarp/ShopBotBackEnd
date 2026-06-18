from fastapi import APIRouter

router = APIRouter(
    prefix="/search",
    tags=["search"]
)

@router.post("")
def search_items(query: str):
    return {"query": query, "results": []}