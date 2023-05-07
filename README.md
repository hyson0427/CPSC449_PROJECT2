# CPSC449 Final Project

## Team Members

- HaYeon SON
- Matt Watkins

## Project Description

Implements a bookstore API using FastAPI and MongoDB. Code is entirely asynchronous
and makes use of aggregation and indexing functionality of MongoDB.

## How to Run

It is assumed that MongoDB is installed and running on the local machine on port 27017.

First, install the dependencies:

```bash
pip install -r requirements.txt
```

Then, generate some random books to test the database:

```bash
python3 book_generator.py
```

Now, run the server. It should be accesible on localhost:8000:

```bash
python3 app.py
```
