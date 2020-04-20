from fastapi import FastAPI

from routers import homework1, user_access

app = FastAPI()
app.include_router(homework1.router, tags=['endpoints for homework1'])
app.include_router(user_access.router, tags=['endpoints for homework1'])

