from sqlalchemy.orm import Session
from .models import User, Team, PullRequest
from .schemas import Team as s_Team, PullRequestCreate
from datetime import datetime
import random

# user crud
def create_user(db: Session, user_id: str, username: str, team_name: str, is_Active: bool):
    user = User(
        user_id=user_id,
        username=username, 
        team_name=team_name, 
        is_active=is_Active)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: str):
    user = db.query(User).filter(User.user_id == user_id).first()
    return user

def get_all_users(db: Session):
    return db.query(User).all()

def update_user_status(db: Session, user_id: str, isActive: bool):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        user.is_active = isActive
        db.commit()
        db.refresh(user)
    return user
def delete_user(db: Session, user_id: str):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        db.delete(user)
    db.commit()
    return user

#team crud
def create_team(db: Session, team: s_Team):
    team_name = team.team_name
    members = team.members
    new_team = db.query(Team).filter(Team.team_name == team_name).first()
    if not new_team:
        db.add(Team(team_name=team_name))
    for member in members:
        user = db.query(User).filter(User.user_id == member.user_id).first()
        if not user:
            db.add(User(
                user_id=member.user_id, 
                team_name=team_name,
                username=member.username,
                is_active=member.is_active))
            
        else:
            user.is_active = member.is_active
            user.username = member.username
            user.team_name = team_name
    
    db.commit()
    db.refresh(new_team)
    return new_team

def get_team(db: Session, team_name: str):
    team = db.query(Team).filter(Team.team_name == team_name).first()
    return team

def get_all_teams(db: Session):
    return db.query(Team).all()

def delete_team(db: Session, team_name: str):
    db.query(User).filter(User.team_name == team_name).update({"team_name": None})
    db.query(Team).filter(Team.team_name == team_name).delete()
    db.commit()


#pull request crud
def select_reviewers(db: Session, author_id: str) -> list[str]:
    author = db.query(User).filter(User.user_id == author_id).first()
    if not author:
        return []
    
    candidates = (
        db.query(User).filter(User.user_id != author_id, 
                              User.team_name == author.team_name,
                              User.is_active == True).all()
    )

    if not candidates:
        return []
    
    selected_users = random.sample(candidates, k=min(2, len(candidates)))
    return [u.user_id for u in selected_users]

def select_replacement_reviewer(db: Session, old_reviewer_id: str) -> str | None:

    old = db.query(User).filter(User.user_id == old_reviewer_id).first()
    if not old:
        return None

    candidates = (
        db.query(User)
        .filter(
            User.team_name == old.team_name,
            User.user_id != old_reviewer_id,
            User.is_active == True
        ).all()
    )

    if not candidates:
        return None

    return random.choice(candidates).user_id

def create_pull_request(db: Session, data: PullRequestCreate):
    reviewers = select_reviewers(db, data.author_id)

    pr = PullRequest(
        pull_request_id=data.pull_request_id,
        pull_request_name=data.pull_request_name,
        author_id=data.author_id,
        status="OPEN",
        assigned_reviewers=reviewers,
        createdAt=datetime.utcnow(),
        mergedAt=None
    )

    db.add(pr)
    db.commit()
    db.refresh(pr)
    return pr

def get_pull_request(db: Session, pr_id: str):
    return db.query(PullRequest).filter(PullRequest.pull_request_id == pr_id).first()

def get_list_pull_requests(db: Session):
    return db.query(PullRequest).all()

def merge_pull_request(db: Session, pr_id: str):
    pull_request = db.query(PullRequest).filter(PullRequest.pull_request_id == pr_id).first()
    if not pull_request:
        return 0
    
    if pull_request.status == "MERGED":
        return pull_request
    
    pull_request.status = "MERGED"
    db.commit()
    db.refresh(pull_request)
    return pull_request

def reassign_reviewer(db: Session, pr_id: str, new_reviewer_id: str):
    pr = db.query(PullRequest).filter(PullRequest.pull_request_id == pr_id).first()
    new_reviewer = db.query(User).filter(User.user_id == new_reviewer_id).first()
    author = db.query(User).filter(User.user_id == pr.author_id).first()
    if new_reviewer_id not in pr.assigned_reviewers and new_reviewer.team_name == author.team_name:
        pr.assigned_reviewers[1] = new_reviewer_id
    
    db.commit()
    return new_reviewer_id

def delete_pr(db: Session, pr_id: str):
    pr = get_pull_request(db, pr_id)
    if not pr:
        return None

    db.delete(pr)
    db.commit()
    return pr
        
    


