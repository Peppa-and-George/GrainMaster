from schema.database import engine
from schema.tables import User
from sqlalchemy.orm import sessionmaker
from auth import verify_password, get_base64_password


class CURD:
    def __init__(self):
        session = sessionmaker(bind=engine)
        self.session = session()
        self.user = UserSchema(self.session)


class UserSchema:
    def __init__(self, session):
        self.__session = session

    def create_user(self, name, phone_number, password):
        user = User(name=name, phone_number=phone_number, hashed_passwd=password)
        self.__session.add(user)
        self.__session.commit()

    def delete_user(self, name):
        if self.get_user(name):
            self.__session.delete(self.get_user(name))
            self.__session.commit()

    def get_user(self, name):
        user = self.__session.query(User).filter_by(name=name).first()
        if not user:
            user = self.__session.query(User).filter_by(phone_number=name).first()
        return user

    def check_user(self, name, password):
        user = self.get_user(name)
        if user:
            if verify_password(password, user.hashed_passwd):
                return user
        return False

    def edit_user(self, name, phone_number):
        user = self.get_user(name)
        if not user:
            user = self.get_user(phone_number)

        user.name = name
        user.phone_number = phone_number
        self.__session.commit()

    def get_users_info(self):
        users = self.__session.query(User).all()
        return users

    def reset_password(self, name, new_password):
        user = self.get_user(name)
        user.hashed_passwd = get_base64_password(new_password)
        self.__session.commit()
