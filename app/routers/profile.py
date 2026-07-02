from fastapi import APIRouter, Depends

from app.core.security import validate_session
from app.database import get_db_connection
from app.schemas.models import GetProfileRequest, TrackProductRequest, UnTrackProductRequest

profile = APIRouter(prefix="/profile", tags=["profile"])

@profile.post("/")
def get_profile(request: GetProfileRequest, conn=Depends(get_db_connection)):
    if validate_session(request.session_id):
        with conn.cursor() as cur:
            cur.execute(
                " SELECT row_to_json(t) FROM (SELECT user_id, username FROM app.profile WHERE username IN (SELECT username FROM app.session WHERE session_id = %s)) t",
                (request.session_id,) 
            )
            result = cur.fetchone()
            cur.execute(
                "SELECT row_to_json(t) FROM (SELECT product_name, product_link, latest_price FROM app.tracked_product WHERE username IN (SELECT username FROM app.session WHERE session_id = %s)) t",
                (request.session_id,)
            )
            tracked_products = cur.fetchall()
            for i in range(len(tracked_products)):
                tracked_products[i] = tracked_products[i][0]
                cur.execute(
                    "SELECT row_to_json(t) FROM (SELECT price, recorded_at FROM app.product_price_history WHERE product_link = %s ORDER BY recorded_at DESC) t",
                    (tracked_products[i]['product_link'],)
                )
                price_history = cur.fetchone()
                if price_history:
                    tracked_products[i]['price_history'] = price_history[1:]
                else:
                    tracked_products[i]['price_history'] = []
        if result:
            return {
                "status": True,
                "user_id": result[0]['user_id'],
                "username": result[0]['username'],
                "tracked_products": tracked_products
            }
        else:
            return {"status": False, "message": "Profile not found."}
    return {"status": False, "message": "Invalid session."}

@profile.post("/track")
def track_product(request: TrackProductRequest, conn=Depends(get_db_connection)):
    if validate_session(request.session_id):
        with conn.cursor() as cur:
            # Check if the product is already being tracked by any user
            cur.execute( "SELECT tracked_product_id FROM app.tracked_product WHERE product_link = %s", (request.product_link,) )
            if id := cur.fetchone():
                # checck if the user is already tracking this product
                cur.execute( "SELECT user_id FROM app.user_tracked_product WHERE user_id = (SELECT user_id FROM app.profile WHERE username = (SELECT username FROM app.session WHERE session_id = %s)) AND tracked_product_id = %s", (request.session_id, id[0]) )
                if cur.fetchone(): 
                    return {"status": False, "message": "Product is already being tracked by this user."}
                # If the product is already being tracked by another user
                else:                                         
                    user_id = cur.fetchone()[0]                         
                    tracked_product_id = id[0]
                    cur.execute( "INSERT INTO app.user_tracked_product (user_id, tracked_product_id) VALUES (%s, %s)", (user_id, tracked_product_id) )
                    return {"status": True, "message": "Product is now being tracked by this user."}
            # If the product is not being tracked by any user
            else:
                # Insert the product into the tracked_product
                cur.execute(
                    "INSERT INTO app.tracked_product (product_link, product_name, latest_price) VALUES ( %s, %s,)",
                    (request.product_link, request.product_name,request.latest_price)
                )
                # Insert the user and product into the user_tracked_product
                cur.execute(
                    """INSERT INTO app.user_tracked_product (user_id, tracked_product_id) VALUES (
                    (SELECT user_id FROM app.profile WHERE username = (
                        SELECT username FROM app.session WHERE session_id = %s
                    ),
                    (SELECT tracked_product_id FROM tracked_product where product_link=%s)
                    )""",
                    (request.session_id, request.product_link)
                )
                # Add the current price as the latest price for the tracking
                cur.execute(
                    """INSERT INTO app.tracked_product_price_history (tracked_product_id, price) VALUES (
                    (SELECT tracked_product_id FROM app.tracked_product where product_link=%s),
                    %s
                    )""",
                    (request.product_link,request.latest_price)
                )
                conn.commit()
                return {"status": True, "message": "Product tracked successfully."}

    return {"status": False, "message": "Invalid session."}

@profile.post("/untrack")
def untrack_product(request: UnTrackProductRequest, conn=Depends(get_db_connection)):
    if validate_session(request.session_id):
        with conn.cursor() as cur:
            # DELETE THE RECORD FROM user_tracked_product
            cur.execute(
                """
                DELETE FROM app.user_tracked_product WHERE user_id=
                SELECT user_id FROM app.profile WHERE username = (
                    SELECT username FROM app.session WHERE session_id = %s) AND
                tracked_product_id=(
                SELECT tracked_product_id FROM app.tracked_product WHERE product_link= %s
                )              
                """,
                (request.session_id,request.product_link)
            )
            conn.commit()
            # check if product isn't being tracked by any users
            cur.execute(
                "SELECT user_id where tracked_product_id=(SELECT tracked_product_id FROM app.tracked_product WHERE product_link= %s)",
                (request.product_link,)
            )
            if not cur.fetchone():
                cur.execute(
                    "DELETE FROM app.tracked_product WHERE tracked_product_id=(SELECT tracked_product_id FROM app.tracked_product WHERE product_link= %s)",
                     (request.product_link,)
                )
            conn.commit()
            return {"message": "Product untracked successfully."}
    return {"status": False, "message": "Invalid session."}
