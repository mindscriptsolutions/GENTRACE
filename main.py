import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.database import init_db
from backend.routers import auth, pedigree, predict, history, profile

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("gentrace")

app = FastAPI(
    title="GeneTrace API",
    description="Pedigree-Driven Hereditary Disease Risk Prediction System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(pedigree.router)
app.include_router(predict.router)
app.include_router(history.router)
app.include_router(profile.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve every HTML page
PAGES = [
    "index", "login", "register", "dashboard", "family",
    "personal", "result", "explainability", "recommendations",
    "history", "profile", "about"
]

for page in PAGES:
    html_path = Path(f"templates/{page}.html")
    _page = page  # capture for closure

    @app.get(f"/{_page}" if _page != "index" else "/", include_in_schema=False)
    def _serve(p=_page):
        f = Path(f"templates/{p}.html")
        return FileResponse(str(f)) if f.exists() else FileResponse("templates/index.html")


@app.on_event("startup")
def startup():
    init_db()
    logger.info("GeneTrace API started. Database initialised.")
