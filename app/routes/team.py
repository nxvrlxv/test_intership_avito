from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import crud
from ..schemas import Team as s_Team, TeamMember, User

router = APIRouter(prefix="/team", tags=["Teams"])

@router.post("/add", response_model=s_Team, status_code=201)
def add_team(team: s_Team, db: Session = Depends(get_db)):
    existing = crud.get_team(db, team.team_name)
    if existing:
        raise HTTPException(status_code=400, detail={
            "error": {"code": "TEAM_EXISTS", "message": "team_name already exists"}
        })
    created_team = crud.create_team(db, team)
    # Обновляем members для ответа
    members: List[TeamMember] = []
    for member in created_team.members:
        members.append(TeamMember(
            user_id=member.user_id,
            username=member.username,
            is_active=member.is_active
        ))
    return s_Team(team_name=created_team.team_name, members=members)

@router.get("/get", response_model=s_Team)
def get_team(team_name: str, db: Session = Depends(get_db)):
    team = crud.get_team(db, team_name)
    if not team:
        raise HTTPException(status_code=404, detail={
            "error": {"code": "NOT_FOUND", "message": "team not found"}
        })
    members: List[TeamMember] = []
    for member in team.members:
        members.append(TeamMember(
            user_id=member.user_id,
            username=member.username,
            is_active=member.is_active
        ))
    return s_Team(team_name=team.team_name, members=members)

@router.delete("/delete")
def delete_team(team_name: str, db: Session = Depends(get_db)):
    team = crud.get_team(db, team_name)
    if not team:
        raise HTTPException(status_code=404, detail={
            "error": {"code": "NOT_FOUND", "message": "team not found"}
        })
    crud.delete_team(db, team_name)
    return {"message": f"Team {team_name} deleted"}
