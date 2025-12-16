from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Synapze AI Backend",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"status": "Backend running 🚀"}
