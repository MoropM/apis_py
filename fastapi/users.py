from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

# Iniciar server: uvicorn users:app --reload
# http://127.0.0.1:8000/

# Entidad User
class User(BaseModel):
    id: int
    name: str
    username: str
    edge: int
    url: str

users_list = [
    User( id = 1, name = "Moroni", username = "moro", edge = 25, url = "https://moroni.com"),
    User( id = 2, name = "Alberto", username = "albert", edge = 29, url = "https://alberto.com"),
    User( id = 3, name = "Jairo", username = "jairo", edge = 32, url = "https://jairo.com")
]
# Funcion encargada de buscar a un usario por su ID
def search_user(id):
    users = filter(lambda user : user.id == id, users_list )
    try:
        return list(users)[0]
    except:
        return {"error": f"No se ha encontrado un usurio con el ID: {id}"}


# Url de ejemplo
@app.get('/usersjson')
async def usersjson():
    return [
        {"name": "Moroni", "username": "moro", "edge": 25, "url": "https://google.com"},
        {"name": "Moroni", "username": "moro23", "edge": 19, "url": "https://google.com"},
        {"name": "Moroni", "username": "moro25", "edge": 32, "url": "https://google.com"}
    ]


@app.get('/users')
async def users():
    return users_list

# Pametros a traves del path
# http://127.0.0.1:8000/user/1
@app.get('/user/{id}')
async def user(id: int):
    return search_user(id)


# Pametros a traves de query
# http://127.0.0.1:8000/userquery/?id=1
@app.get('/userquery')
async def user(id: int):
    return search_user(id)


@app.post('/user/')
async def user(user: User):
    if type(search_user(user.id)) == User:
        return {"error": "El usuario ya existe"}
    else:
        users_list.append(user)

