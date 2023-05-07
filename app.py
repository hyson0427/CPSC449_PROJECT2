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
    await book_collection.create_index("title")
    await book_collection.create_index("author")
    await book_collection.create_index("price")
    await book_collection.create_index("stock")

    # Create a compond index for usage with the search endpoint
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
        [{"stock": {"$gt": 0}}, {"$sort": {"stock": -1}}, {"$limit": 5}]
    ).to_list(length=None)
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
    result = await book_collection.find(query)
    found_books = await result.to_list(length=None)

    return found_books


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8080)
