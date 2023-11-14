import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.responses import RedirectResponse
from fastapi.security.api_key import APIKeyHeader

# ---------------------------------------------------------------------------------------------------------
# Пример реализации самой простой аутентификации. Не рекомендуется использовать в нелокальных проектах т.к.
# ключ незахеширован и остается в header'е запроса
# ---------------------------------------------------------------------------------------------------------

app = FastAPI()
api_key_header = APIKeyHeader(name="Authorization", auto_error=True)

SECRET_KEY = "api_secret_key"  # Секретный ключ


async def get_api_key(api_key: str = Security(api_key_header)):
    """
    Функция проверки секретного ключа, получаемого в header запроса

    :param api_key: api-ключ
    :return:
    """
    if api_key == SECRET_KEY:
        return api_key
    else:
        raise HTTPException(status_code=401, detail="Невалидный API ключ")


# Тестовый эндпоинт
@app.get("/test", dependencies=[Depends(get_api_key)])
async def test(name: str):
    return f"Hello, {name}!"


# Эндпоинт документации
@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


if __name__ == '__main__':
    uvicorn.run(app)
