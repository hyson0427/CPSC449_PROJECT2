from typing import Optional

import pymongo.errors
from bson import ObjectId, errors
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

app = FastAPI()
mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
database = mongo_client["bookstore"]
book_collection = database["books"]


class Book(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    price: int = Field(..., ge=0)
    stock: int = Field(..., ge=0)


# Generates all of the indices in MongoDB
async def create_indices():
    await book_collection.create_index(
        "title", unique=True
    )  # Only one book of the same title
    await book_collection.create_index("author")
    await book_collection.create_index("price")
    await book_collection.create_index("stock")

    # Create a compound index for usage with the search endpoint
    await book_collection.create_index([("title", 1), ("author", 1), ("price", 1)])


# Create all indices on startup
@app.on_event("startup")
async def on_startup():
    await create_indices()


# GET /books: Retrieves a list of all books in the store
@app.get("/books")
async def get_all_books():
    result = book_collection.find({})
    all_books = await result.to_list(length=None)

    # Change all object ids to strings. Otherwise this will cause an error
    # because FastAPI cannot serialize object ids
    all_books = [stringify_object_id(book) for book in all_books]

    return all_books


# GET /book_count: Retrieves the total number of books in the store
@app.get("/book_count")
async def get_book_count():
    count = await book_collection.aggregate([{"$count": "total_books"}]).to_list(
        length=None
    )
    return count[0]["total_books"]


# GET /bestsellers: Retrieves a list of the top 5 best-selling books
# (meaning books that have the lowest stock)
@app.get("/bestsellers")
async def get_bestsellers():
    result = await book_collection.aggregate(
        [{"$match": {"stock": {"$gt": 0}}}, {"$sort": {"stock": 1}}, {"$limit": 5}]
    ).to_list(length=None)

    # Change all object ids to strings. Otherwise this will cause an error
    # because FastAPI cannot serialize object ids
    result = [stringify_object_id(book) for book in result]

    return result


# GET /top_authors: Retrieves a list of the top 5 authors
@app.get("/top_authors")
async def get_top_authors():
    result = await book_collection.aggregate(
        [
            {"$group": {"_id": "$author", "total_books": {"$sum": 1}}},
            {"$sort": {"total_books": -1}},
            {"$limit": 5},
        ]
    ).to_list(length=None)
    return result


# GET /books/{book_id}: Retrieves a specific book by ID
@app.get("/books/{book_id}")
async def get_book_by_id(book_id: str):
    try:
        result = await book_collection.find_one({"_id": ObjectId(book_id)})
    except errors.InvalidId:
        return {"Result": "Invalid book id specified."}

    return stringify_object_id(result) if result else {"Result": "No book found."}


# POST /books: Adds a new book to the store
@app.post("/books")
async def add_new_book(book: Book):
    try:
        await book_collection.insert_one(book.dict())
    except pymongo.errors.DuplicateKeyError:
        return {"Result": "Book with this title already exists."}
    except Exception:
        return {"Result": "Failed to add book."}

    return {"Result": "Successfully added book."}


# PUT /books/{book_id}: Updates an existing book by ID
@app.put("/books/{book_id}")
async def update_book_by_id(book_id: str, book: Book):
    result = await book_collection.update_one(
        {"_id": ObjectId(book_id)}, {"$set": book.dict()}
    )
    return (
        {"Result": f"Successfully updated book {book_id}."}
        if result.modified_count == 1
        else {"Result": f"Failed to update book {book_id}."}
    )


# DELETE /books/{book_id}: Deletes a book from the store by ID
@app.delete("/books/{book_id}")
async def delete_book_by_id(book_id: str):
    result = await book_collection.delete_one({"_id": ObjectId(book_id)})
    return (
        {"Result": f"Successfully deleted book {book_id}."}
        if result.deleted_count == 1
        else {"Result": f"Failed to delete book {book_id}."}
    )


def stringify_object_id(book):
    book["_id"] = str(book["_id"])
    return book


# GET /search?title={}&author={}&min_price={}&max_price={}: Searches for books
# by title, author, and price range
@app.get("/search")
async def search_books(
    title: Optional[str] = "",
    author: Optional[str] = "",
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
):
    query = {}
    if title:
        query["title"] = {"$regex": title, "$options": "i"}
    if author:
        query["author"] = {"$regex": author, "$options": "i"}
    if min_price or max_price:
        price_query = {}
        if min_price:
            price_query["$gte"] = min_price
        if max_price:
            price_query["$lte"] = max_price
        query["price"] = price_query
    result = book_collection.find(query)
    found_books = await result.to_list(length=None)

    # Change all object ids to strings. Otherwise this will cause an error
    # because FastAPI cannot serialize object ids
    found_books = [stringify_object_id(book) for book in found_books]

    return found_books if found_books else {"Result": "No books found."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
