#  Documentación oficial: https://fastapi.tiangolo.com/es
# Instalar FastAPI: pip install "fastapi[all]"
# Trabajar con JWT:   pip install "python-jose[cryptography]"
# Para encriptación:  pip install "passlib[bcrypt]"

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
# Módulo de autenticación
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1 # 1 minuto
# openssl rand -hex 32 : Generar un str random seguro
SECRET = "52f60c0df49a66786ee49d0d66123dbc738d3d0209d34de52a2776c46714b29d"

# Iniciar API Router
routerJwtAuth = APIRouter(
    prefix= '/jwt_auth',
    tags= ['jwt_auth'],
    responses={
        404: { "message": "No encontrado"}
    }
)


# OAuth2PasswordBearer : Clase encargada de gestionar la Autenticación
# OAuth2PasswordRequestForm : Clase encargada de capturar la contraseña
oauth2 = OAuth2PasswordBearer( tokenUrl="login" )


crypt = CryptContext(schemes=["bcrypt"])

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
        "disabled": True,
        "password": "$2a$12$MfP.HGqemooWtMJLZFjr4.L5deCeU25SHOyZUC9HLJOvADi4SJd/6" #123456
    },
    "moroni2": {
        "username": "moroni2",
        "full_name": "Moroni Perez",
        "email": "moroni2@mail.com",
        "disabled": False,
        "password": "$2a$12$ydrOsCEjrE/tijQINziHA.BPgjnijW1qYJdktJLXFT8bUHi5.ZVw2" #987654
    }
}

# Buscar usuarios en BD
def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])


def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])


# Proceso de Validación de Token y obtención de usuario
async def auth_user( token: str = Depends(oauth2) ):
    exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticación inválidas",
            headers={"WWW-Authenticate": "Bearer"})
    try:
        # Desencriptar token
        username = jwt.decode(token, SECRET, algorithms=ALGORITHM).get("sub")
        if username is None:
            raise exception

    except JWTError:
        raise exception

    return search_user(username)



# Función para criterio de Dependencia
async def current_user(user: User = Depends(auth_user) ):
    # Verificando usuario activo
    if not user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uusario inactivo")

    return user



@routerJwtAuth.get('/log')
async def log():
    return "Probando ruta del sistema"


@routerJwtAuth.post('/login_jwt')
async def login_jwt(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    
    if not user_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")

    user = search_user_db(form.username)

    # if not form.password == user.password:
    # verify(Pass_original, Pass_encriptada)
    if not crypt.verify(form.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcta")
 

    # Generar un token seguro. 1 min más de la fecha de creación
    # Tiempo en que expirará el Token. La hora actual + 1 min
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)

    access_token = {
        "sub": user.username,
        "exp": expire
    }
    # access_token_expiration =
    # Usuario autenticado
    return {
        "access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM),
        "token_type": "bearer"
    }



@routerJwtAuth.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user


