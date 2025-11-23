from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import crud
from ..schemas import PullRequestCreate, PullRequestShort


router = APIRouter(prefix="/pullRequest", tags=["PullRequests"])

# Создание PR и автоматический выбор ревьюверов
@router.post("/create", response_model=PullRequestCreate, status_code=201)
def create_pr(data: PullRequestCreate, db: Session = Depends(get_db)):
    existing = crud.get_pull_request(db, data.pull_request_id)
    if existing:
        raise HTTPException(status_code=409, detail={
            "error": {"code": "PR_EXISTS", "message": "PR id already exists"}
        })
    
    # Проверяем автора
    author = crud.get_user(db, data.author_id)
    if not author or not author.team_name:
        raise HTTPException(status_code=404, detail={
            "error": {"code": "NOT_FOUND", "message": "author or team not found"}
        })
    
    pr = crud.create_pull_request(db, data)
    return pr

# Пометить PR как MERGED
@router.post("/merge", response_model=PullRequestCreate)
def merge_pr(pull_request_id: str, db: Session = Depends(get_db)):
    pr = crud.get_pull_request(db, pull_request_id)
    if not pr:
        raise HTTPException(status_code=404, detail={
            "error": {"code": "NOT_FOUND", "message": "PR not found"}
        })
    pr = crud.merge_pull_request(db, pull_request_id)
    return pr


@router.post("/reassign")
def reassign_reviewer(pull_request_id: str, old_reviewer_id: str, db: Session = Depends(get_db)):
    pr = crud.get_pull_request(db, pull_request_id)
    if not pr:
        raise HTTPException(status_code=404, detail={
            "error": {"code": "NOT_FOUND", "message": "PR not found"}
        })
    old_reviewer = crud.get_user(db, old_reviewer_id)
    if not old_reviewer:
        raise HTTPException(status_code=404, detail={
            "error": {"code": "NOT_FOUND", "message": "user not found"}
        })
    if pr.status == "MERGED":
        raise HTTPException(status_code=409, detail={
            "error": {"code": "PR_MERGED", "message": "cannot reassign on merged PR"}
        })
    if old_reviewer_id not in pr.assigned_reviewers:
        raise HTTPException(status_code=409, detail={
            "error": {"code": "NOT_ASSIGNED", "message": "reviewer is not assigned to this PR"}
        })
    
    new_reviewer_id = crud.select_replacement_reviewer(db, old_reviewer_id)
    if not new_reviewer_id:
        raise HTTPException(status_code=409, detail={
            "error": {"code": "NO_CANDIDATE", "message": "no active replacement candidate in team"}
        })
    
    # Меняем ревьювера
    index = pr.assigned_reviewers.index(old_reviewer_id)
    pr.assigned_reviewers[index] = new_reviewer_id
    db.commit()
    db.refresh(pr)
    return {"pr": pr, "replaced_by": new_reviewer_id}
