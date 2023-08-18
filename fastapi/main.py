#  Documentación oficial: https://fastapi.tiangolo.com/es
# Instalar FastAPI: pip install "fastapi[all]"
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# Importar fichero
# from Nombre_Path import Nombre_fichero
from routers import products, users, basic_auth_users
# Exponer nuestros archivos estaticos
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Rutas
app.include_router(products.router)
app.include_router(users.routerUser)
app.include_router(basic_auth_users.routerAuth)

# Exponer nuestros archivos estaticos
app.mount("/static", StaticFiles(directory="static"), name="static")




# Validacion de libros
class Books(BaseModel):
    title: str
    date: str
    pages: int
    description: Optional[str]

@app.get('/')
async def index():
    return {"message": f"Hola, Hola!!"}

@app.get('/books/{id}')
async def books(id: int):
    return { "data": id }

@app.post('/books')
async def insert_book(book: Books):
    return {
        "message": f"El libro {book.title} a sido insertado"
    }


#https://fastapi.tiangolo.com/
# Iniciar server: uvicorn main:app --reload
# http://127.0.0.1:8000/