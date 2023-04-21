from fastapi import FastAPI
from src import routers
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers.router)

#app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/static", StaticFiles(directory="static"), name="static")
