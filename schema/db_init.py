from schema.database import Base, engine
from user import User

Base.metadata.create_all(engine)
