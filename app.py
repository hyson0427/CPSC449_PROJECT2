from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

app = FastAPI()
mongo = AsyncIOMotorClient("mongodb://localhost:27017")


class Book(BaseModel):
    title: str
    author: str
    description: str
    price: int
    stock: int


# GET /books: Retrieves a list of all books in the store
@app.get("/books")
async def get_all_books():
    mongo["bookstore"]["books"].find({})


# GET /books/{book_id}: Retrieves a specific book by ID
@app.get("/books/{book_id}")
async def get_book_by_id(book_id: int):
    mongo["bookstore"]["books"].find_one({"_id": book_id})


# POST /books: Adds a new book to the store
@app.post("/books")
async def add_new_book(book: Book):
    mongo["bookstore"]["books"].insert_one(book.dict())


# PUT /books/{book_id}: Updates an existing book by ID
@app.put("/books/{book_id}")
async def update_book_by_id(book_id: int, book: Book):
    mongo["bookstore"]["books"].update_one({"_id": book_id}, {"$set": book.dict()})


# DELETE /books/{book_id}: Deletes a book from the store by ID
@app.delete("/books/{book_id}")
async def delete_book_by_id(book_id: int):
    mongo["bookstore"]["books"].delete_one({"_id": book_id})


# GET /search?title={}&author={}&min_price={}&max_price={}: Searches for books
# by title, author, and price range
@app.get("/search")
async def search_books(
    title: str | None = None,
    author: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
):
    query = {}
    if title:
        query["title"] = title
    if author:
        query["author"] = author
    if min_price:
        query["price"] = {"$gte": min_price}
    if max_price:
        query["price"] = {"$lte": max_price}
    result = mongo["bookstore"]["books"].find(query)

    found_books = []
    for book in result:
        found_books.append(book)

    return found_books
