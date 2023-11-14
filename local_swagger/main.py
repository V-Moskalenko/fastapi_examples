import pathlib

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html

# ---------------------------------------------------------------------------------------------------------
# Пример разворачивания локального Swagger
# ---------------------------------------------------------------------------------------------------------


app = FastAPI(docs_url=None, redoc_url=None, version='1.0.0')

project_folder_path = pathlib.Path(__file__).parents[1]
path_to_static = pathlib.Path(project_folder_path, 'resources', 'static')


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title='My API',
        version='1.0.0',
        openapi_version='3.0.0',
        description="This custom SWAGGER documentation",
        routes=app.routes
    )
    openapi_schema["info"]["x-logo"] = {"url": "/static/flaticon_cache_icon.png"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
app.mount("/static", StaticFiles(directory=path_to_static), name="static")


@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js"
    )


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/favicon-32x32.png"
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/test")
async def test(name: str):
    return f"Hello, {name}!"


if __name__ == '__main__':
    uvicorn.run(app)
