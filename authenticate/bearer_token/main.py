from datetime import datetime, timedelta
from typing import Union

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasicCredentials, HTTPBearer
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from pydantic import BaseModel

# ---------------------------------------------------------------------------------------------------------
# Пример реализации Bearer аутентификации
# ---------------------------------------------------------------------------------------------------------

app = FastAPI()
security = HTTPBearer()

SECRET_KEY = "api_secret_key"  # Секретный ключ хеширования
ALGORITHM = "HS256"  # Алгоритм JWT хеширования
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Время жизни токена


# Объявим тестовую БД - USERS, которая будет содержать пользователей: объект класса User
class User(BaseModel):
    username: str
    password: str


USERS = [User(username='one', password='secret_one'), User(username='two', password='secret_two')]


def get_user(username: str, users_list: list[User]) -> User | bool:
    """
    Функция проверки существования пользователя в БД, по username.

    :param username: логин пользователя, передаваемый в запросе
    :param users_list: список пользователей БД
    :return: объект класса User, если пользователь был найден, иначе False
    """
    for user in users_list:
        if username in user.username:
            return user
    return False


def create_access_token(expires_delta: Union[timedelta, None] = None) -> str:
    """
    Метод создания токена

    :param expires_delta: время жизни токена в timedelta
    :return: Токен
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expiration_time = {"exp": expire}
    encoded_jwt = jwt.encode(expiration_time, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def check_access_token(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Функция проверки валидности токена

    :param credentials: зависимость fastapi.security
    :return:
    """
    # Определим ошибку
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials (некорректный или недействительный токен)",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM,
                             options={"verify_signature": False, "verify_aud": False, "verify_iss": False})
        if payload is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception


# Response-модель Токена
class Token(BaseModel):
    access_token: str
    token_type: str


# Эндпоинт получения Токена
@app.post("/token", response_model=Token)
async def action_create_access_token(username: str, password: str):
    user = get_user(username, USERS)  # Проверим наличие пользователя в БД
    if not user:
        raise HTTPException(status_code=400, detail="Данный пользователь отсутствует в базе")
    if password != user.password:
        raise HTTPException(status_code=400, detail=f"Некорректный пароль для пользователя: {user.username}")

    # Сформируем токен
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


# Тестовый эндпоинт
@app.get("/test", dependencies=[Depends(check_access_token)])
async def test(name: str):
    return f"Hello, {name}!"


# Эндпоинт документации
@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


if __name__ == '__main__':
    uvicorn.run(app)
