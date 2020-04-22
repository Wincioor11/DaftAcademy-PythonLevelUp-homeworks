from fastapi import FastAPI

from routers import patients, user_access

app = FastAPI()
app.include_router(patients.router, tags=['endpoints for homework1'])
app.include_router(user_access.router, tags=['endpoints for homework1'])

