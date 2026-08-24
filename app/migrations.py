from app.core.database import Base, engine
from app.modules.user.models import User, UserType
from app.modules.authentication.models import UserAuthToken


def run_migrations():
    Base.metadata.create_all(bind=engine)
