from fastapi import APIRouter

router = APIRouter()

@router.post("/analyze")
def analyze_resume():
    return {"message": "Resume analyzer coming soon"}
