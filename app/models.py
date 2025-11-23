from sqlalchemy import create_engine,  Column, Integer, String, Boolean, DateTime, ForeignKey, ARRAY, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class Team(Base):
    __tablename__ = "team"

    team_name = Column(String, primary_key=True)

    members=relationship("User", back_populates="team")

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)
    username = Column(String, nullable=False)
    team_name = Column(String, ForeignKey("team.team_name"), nullable=True)
    is_active = Column(Boolean, default=True)

    team = relationship("Team", back_populates="members")
    user_prs = relationship("PullRequest", back_populates="author")


class PullRequest(Base):
    __tablename__ = "pull_request"

    pull_request_id = Column(String, primary_key=True)
    pull_request_name = Column(String, nullable=False)
    author_id = Column(String, ForeignKey("users.user_id"),nullable=False)
    status = Column(String, nullable=False)
    assigned_reviewers = Column(JSON)
    createdAt = Column(DateTime)
    mergedAt = Column(DateTime)

    author = relationship("User", back_populates="user_prs")

