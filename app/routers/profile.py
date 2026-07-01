from fastapi import APIRouter

profile = APIRouter(prefix="/profile", tags=["profile"])

@profile.post("/")
def get_profile():
    pass

@profile.post("/track")
def track_product():
    pass

@profile.post("/untrack")
def untrack_product():
    pass

@profile.post("/tracked")
def get_tracked_products():
    pass
