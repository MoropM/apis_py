#  APIRouter : Permite expandir las rutas a otros ficheros donde se llame FastAPI
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional


# https://www.youtube.com/watch?v=_y9qQZXE24A&t=10802s

routerUser = APIRouter(
    prefix= '/users',
    tags= ['users'],
    responses={
        404: { "message": "No encontrado"}
    }
)

#https://fastapi.tiangolo.com/
# Iniciar server: uvicorn users:app --reload
# http://127.0.0.1:8000/
#  Crear archivo de requerimientos:  pip freeze > requirements.txt

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
"""
@routerUser.get('/usersjson')
async def usersjson():
    return [
        {"name": "Moroni", "username": "moro", "edge": 25, "url": "https://google.com"},
        {"name": "Moroni", "username": "moro23", "edge": 19, "url": "https://google.com"},
        {"name": "Moroni", "username": "moro25", "edge": 32, "url": "https://google.com"}
    ]
"""


@routerUser.get('/')
async def users():
    return users_list


# Pametros a traves del path
# http://127.0.0.1:8000/user/1
@routerUser.get('/{id}')
async def user(id: int):
    return search_user(id)


# Pametros a traves de query
# http://127.0.0.1:8000/userquery/?id=1
@routerUser.get('/userquery')
async def user(id: int):
    return search_user(id)


@routerUser.post('/', response_model=User, status_code=201)
async def user(user: User):
    if type(search_user(user.id)) == User:
        # return {"error": "El usuario ya existe"}
        # raise : Retorna correctamente el error
        raise HTTPException(status_code=404, detail="El usuario ya existe")
    else:
        users_list.append(user)
        return user


@routerUser.put('/')
async def user(user: User):
    found = False
    for index, saved_user in enumerate(users_list):
        if saved_user.id == user.id:
            users_list[index] = user
            found = True

    if not found:
        return {
            "error": "No se ha actualizado el usuario"
        }
    else:
        return user


@routerUser.delete('/{id}')
async def user(id: int):
    found = False
    for index, saved_user in enumerate(users_list):
        if saved_user.id == id:
            del users_list[index]
            found = True

    if not found:
        return { "error": "No se ha eliminado el usuario" }
    else:
        return { "succes": "Usuario eliminado" }

