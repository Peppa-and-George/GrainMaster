from schema.tables import User
from schema.database import sessionmaker, engine
from auth import get_base64_password, verify_password
session = sessionmaker(bind=engine)()

# default_user = User(name="admin", phone_number=111111, hashed_passwd=get_base64_password("Admin@123!"))
# session.add(default_user)
# session.commit()


user = session.query(User).filter(User.name=="admin").first()


print(verify_password('Admin@123!', user.hashed_passwd))