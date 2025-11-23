import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Team, User
from app.database import engine  


Session = sessionmaker(bind=engine)
db = Session()

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
