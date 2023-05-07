from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

app = FastAPI()
mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
database = mongo_client["bookstore"]
book_collection = database["books"]


class Book(BaseModel):
    title: str
    author: str
    description: str
    price: int
    stock: int


# GET /books: Retrieves a list of all books in the store
@app.get("/books")
async def get_all_books():
    result = await book_collection.find({})
    all_books = await result.to_list(length=None)

    return all_books


# GET /books/{book_id}: Retrieves a specific book by ID
@app.get("/books/{book_id}")
async def get_book_by_id(book_id: int) -> Book:
    return await book_collection.find_one({"_id": book_id})


# POST /books: Adds a new book to the store
@app.post("/books")
async def add_new_book(book: Book):
    await book_collection.insert_one(book.dict())


# PUT /books/{book_id}: Updates an existing book by ID
@app.put("/books/{book_id}")
async def update_book_by_id(book_id: int, book: Book):
    await book_collection.update_one({"_id": book_id}, {"$set": book.dict()})


# DELETE /books/{book_id}: Deletes a book from the store by ID
@app.delete("/books/{book_id}")
async def delete_book_by_id(book_id: int):
    await book_collection.delete_one({"_id": book_id})


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
    result = await database["books"].find(query)
    found_books = await result.to_list(length=None)

    return found_books
