from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Max",
    description="""potom dobavlyu!""", # !
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "Eiztrips",
        "url": "https://eiztrips.dev",
        "email": "eiztrips.dev@yandex.ru"
    }
)

# bla bla bla middleware CORS debug mode
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}