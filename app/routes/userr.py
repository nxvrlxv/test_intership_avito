from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud
from ..schemas import User, PullRequestShort
from ..models import PullRequest

user_router = APIRouter(prefix="/users", tags=["Users"])

@user_router.post("/", response_model=User)
def create_user_endpoint(user: User, db: Session = Depends(get_db)):
    return crud.create_user(
        db=db,
        user_id=user.user_id,
        username=user.username,
        team_name=user.team_name,
        is_Active=user.is_active
    )

@user_router.get("/all_users", response_model=list[User])
def get_all_users(db: Session = Depends(get_db)):
    return crud.get_all_users(db)

@user_router.post("/setIsActive", response_model=User)
def set_user_active(user_id: str, is_active: bool, db: Session = Depends(get_db)):
    user = crud.update_user_status(db, user_id, is_active)
    if not user:
        raise HTTPException(404, detail={"error": {"code": "NOT_FOUND", "message": "User not found"}})
    return user

@user_router.get("/getReview")
def get_user_reviews(user_id: str, db: Session = Depends(get_db)):
    all_prs = db.query(PullRequest).all()
    assigned_prs = [
        PullRequestShort.model_validate(pr) 
        for pr in all_prs 
        if user_id in (pr.assigned_reviewers or [])
    ]
    return {"user_id": user_id, "pull_requests": assigned_prs}

@user_router.get("/{user_id}", response_model=User)
def get_user_endpoint(user_id: str, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(404, detail={"error": {"code": "NOT_FOUND", "message": "User not found"}})
    return user