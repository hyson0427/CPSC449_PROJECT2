import random

import requests
from pymongo import MongoClient

from app import Book

random_author_names = [
    "Arnold Kain",
    "Dorian Chapman",
    "Leopold Rios",
    "Valentine Marrow",
    "Hope Ingram",
    "Norris Hale",
    "Ulric Ogley",
    "Darcy Tillery",
    "Clara Vaughn",
    "Jasmine Hunter",
    "Henrietta Hubbard",
    "Regina Clark",
    "Chandler Gray",
    "Neil Salazar",
]


# Generates random words, sentences, titles and authors using an online word list
class RandomGenerator:
    WORD_LIST_URL = "https://www.mit.edu/~ecprice/wordlist.10000"

    def __init__(self):
        response = requests.get(self.WORD_LIST_URL)
        self.word_list = response.text.splitlines()

    def get_random_word(self) -> str:
        return random.choice(self.word_list)

    def get_random_author(self) -> str:
        return random.choice(random_author_names)

    def get_random_title(self) -> str:
        return (
            " ".join(self.get_random_word() for _ in range(random.randint(1, 3)))
        ).title()

    def get_random_sentence(self) -> str:
        return (
            " ".join(self.get_random_word() for _ in range(random.randint(5, 10))) + "."
        ).capitalize()

    def get_random_description(self) -> str:
        return " ".join(
            [self.get_random_sentence() for _ in range(random.randint(1, 3))]
        )


# Adds a specified number of random books to the database
def add_random_books_to_database(count: int):
    client = MongoClient("mongodb://localhost:27017")
    db = client["bookstore"]
    book_collection = db["books"]

    for i in range(count):
        book = generate_random_book()
        book_collection.insert_one(book.dict())


# Generates a single random book
def generate_random_book() -> Book:
    r = RandomGenerator()
    title = r.get_random_title()
    author = r.get_random_author()
    description = r.get_random_description()

    book = Book(
        title=title,
        author=author,
        description=description,
        price=random.randrange(9, 35),
        stock=random.randrange(0, 30),
    )

    return book


# Add random books to the database when this file is run
if __name__ == "__main__":
    add_random_books_to_database(10)
