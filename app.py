from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

# from pymongo import MongoClient

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
    pass


# GET /books/{book_id}: Retrieves a specific book by ID
@app.get("/books/{book_id}")
async def get_book_by_id(book_id: int):
    pass


# POST /books: Adds a new book to the store
@app.post("/books")
async def add_new_book(book: Book):
    pass


# PUT /books/{book_id}: Updates an existing book by ID
@app.put("/books/{book_id}")
async def update_book_by_id(book_id: int, book: Book):
    pass


# DELETE /books/{book_id}: Deletes a book from the store by ID
@app.delete("/books/{book_id}")
async def delete_book_by_id(book_id: int):
    pass


# GET /search?title={}&author={}&min_price={}&max_price={}: Searches for books by title, author, and price range
@app.get("/search")
async def search_books(
    title: str | None = None,
    author: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
):
    pass
    pass
