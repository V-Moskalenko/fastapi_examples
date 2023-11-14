from datetime import datetime, timedelta
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt

# ---------------------------------------------------------------------------------------------------------
# Пример реализации аутентификации Oauth2.
# ---------------------------------------------------------------------------------------------------------

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "api_secret_key"  # Секретный ключ хеширования
ALGORITHM = "HS256"  # Алгоритм JWT хеширования
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Время жизни токена


# Объявим тестовую БД - USERS, которая будет содержать пользователей: объект класса User
class User(BaseModel):
    username: str
    hashed_password: str


def get_password_hash(password: str) -> str:
    """
    Функция хеширования пароля

    :param password: нехешированный пароль
    :return: хешированный пароль
    """
    return pwd_context.hash(password)


# Важно! В базе не должны содержатся нехешированные пароли, в данном примере пароль хешируется непосредственно в классе
USERS = [User(username='one', hashed_password=get_password_hash('secret_one')),
         User(username='two', hashed_password=get_password_hash('secret_two'))]


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


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Функция сверки хешированных паролей

    :param plain_password: нехешированный пароль
    :param hashed_password: хешированный пароль из БД
    :return: True - пароли валидны, False - пароли не валидны
    """
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str) -> User | bool:
    """
    Функция аутентификации пользователя.

    :param username: имя пользователя
    :param password: пароль пользователя
    :return: Объект User или False
    """
    user = get_user(username, USERS)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Метод создания токена

    :param data: {"sub": user.username}
    :param expires_delta: время жизни токена
    :return:
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Функция получения валидного пользователя из БД

    :param token: Токен
    :return:
    """
    # Определим ошибку
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials (некорректный или недействительный токен)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username, users_list=USERS)
    if user is None:
        raise credentials_exception
    return user


# Эндпоинт получения Токена. Важно в данную модель RequestForm передаётся нехешированный пароль
@app.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Тестовый эндпоинт
@app.get("/test", dependencies=[Depends(get_current_user)])
async def test(name: str):
    return f"Hello, {name}!"


# Эндпоинт документации
@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


if __name__ == '__main__':
    uvicorn.run(app)
