from app.database.db import Base, engine
from app.models.user import User
from app.models.certificate import Certificate


def init_database():
    Base.metadata.create_all(bind=engine)
    print("Database Created Successfully")


if __name__ == "__main__":
    init_database()