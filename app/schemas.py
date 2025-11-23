from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum


class Status(str, Enum):
    OPEN = "OPEN"
    MERGED = "MERGED"


class User(BaseModel):
    user_id: str
    username: str
    team_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes: True

class TeamMember(BaseModel):
    user_id: str
    username: str
    is_active: bool

class Team(BaseModel):
    team_name: str
    members: Optional[List[TeamMember]] = None

class PullRequestCreate(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: Status
    assigned_reviewers: List[str]
    createdAt: Optional[datetime] = None
    mergedAt: Optional[datetime] = None

class PullRequestShort(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: Status

    model_config = ConfigDict(from_attributes=True)


