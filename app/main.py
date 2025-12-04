from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import router
from middleware import SecurityHeaders, RateLimit

load_dotenv()

app = FastAPI()

app.add_middleware(SecurityHeaders)
app.add_middleware(RateLimit)

app.include_router(router)


base_dir = Path(__file__).resolve().parent.parent
static_dir = base_dir / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
