from fastapi import FastAPI
from routers import v1_0

app = FastAPI()


app.include_router(v1_0.router, prefix="/alice/v1.0")
