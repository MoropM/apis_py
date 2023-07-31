from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
# Iniciar server: uvicorn main:app --reload
# http://127.0.0.1:8000/

# Validacion de libros
class Books(BaseModel):
    title: str
    date: str
    pages: int
    description: Optional[str]

@app.get('/')
async def index():
    return {"message": f"Hola, Mundo"}

@app.get('/books/{id}')
async def books(id: int):
    return {
        "data": id
    }

@app.post('/books')
async def insert_book(book: Books):
    return {
        "message": f"El libro {book.title} a sido insertado"
    }