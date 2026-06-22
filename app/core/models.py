from pydantic import BaseModel

class Product(BaseModel):
    name:  str
    rating: float
    price: float
    link: str
    image: str
    description: str

class Search(BaseModel):
    product_search: str
    