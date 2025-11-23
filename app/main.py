from fastapi import FastAPI
from .routes import userr, team, pr
from .database import init_db
import random
from sqlalchemy.orm import sessionmaker
from app.models import Base, Team, User
from app.database import engine


app = FastAPI(title="PR Reviewer Assignment Service (Test Task, Fall 2025)", version="1.0.0")

app.include_router(userr.user_router)
app.include_router(team.router)
app.include_router(pr.router)
@app.on_event("startup")
def on_startup():
    init_db()

    Session = sessionmaker(bind=engine)
    db = Session()
  
    if db.query(Team).first():
        print("Данные уже есть в БД — пропускаем сид")
        db.close()
        return


    db.query(User).delete()
    db.query(Team).delete()

    print("Сидим тестовые данные...")

    for i in range(1, 21):
        team_name = f"team_{i:02d}"
        db.add(Team(team_name=team_name))

        for j in range(random.randint(8, 15)):
            num = db.query(User).count() + 1
            db.add(User(
                user_id=f"user_{num}",
                username=f"user{num}",
                team_name=team_name,
                is_active=random.choice([True, True, True, False])
            ))

    db.commit()
    db.close()
