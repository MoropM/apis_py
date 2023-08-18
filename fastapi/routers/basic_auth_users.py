from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
# Módulo de autenticación
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

routerAuth = APIRouter(
    prefix= '/auth',
    tags= ['auth'],
    responses={
        404: { "message": "No encontrado"}
    }
)

# OAuth2PasswordBearer : Clase encargada de gestionar la Autenticación
# OAuth2PasswordRequestForm : Clase encargada de capturar la contraseña
oauth2 = OAuth2PasswordBearer( tokenUrl="login" )


# Entidad User
class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool

class UserDB(User):
    password: str

users_db = {
    "moroni": {
        "username": "moroni",
        "full_name": "Moroni Perez",
        "email": "moroni@mail.com",
        "disabled": False,
        "password": "123456"
    },
    "moroni2": {
        "username": "moroni2",
        "full_name": "Moroni Perez",
        "email": "moroni2@mail.com",
        "disabled": True,
        "password": "987654"
    }
}


def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])

def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])

# Función para criterio de Dependencia
async def current_user(token: str = Depends(oauth2) ):
    user = search_user(token)
    # Verificando la utorización del usuario
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticación inválidas",
            headers={"WWW-Authenticate": "Bearer"})
    
    # Verificando usuario activo
    if not user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uusario inactivo")

    return user


@routerAuth.post('/login')
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")

    user = search_user_db(form.username)
    if not form.password == user.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcta")
    
    # Usuario autenticado
    return {
        "access_token": user.username,
        "token_type": "bearer"
    }

@routerAuth.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user
