
from app.database import Base, engine
from app import models, energy_models, platform_models


def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("WattWise database tables created successfully!")


if __name__ == "__main__":
    initialize_database()
