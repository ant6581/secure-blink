import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import router

load_dotenv()

app = FastAPI()

app.include_router(router)


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(base_dir, "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
