from db.database import SessionLocal
from utils.auth import AuthUtils
import os
from db.model import User, UserTypeEnum
from sqlalchemy import or_

admin_init_login = os.getenv("ADMIN_INIT_LOGIN", "admin")
admin_init_password = os.getenv("ADMIN_INIT_PASSWORD", "automate123.")

superuser_init_login = os.getenv("SUPERUSER_INIT_LOGIN", "superuser")
superuser_init_password = os.getenv("SUPERUSER_INIT_PASSWORD", "superuser123.")

user_init_login = os.getenv("USER_INIT_LOGIN", "user")
user_init_password = os.getenv("USER_INIT_PASSWORD", "user123.")


def initializer_inserts():
    session = SessionLocal()
    try:
        admin_hash_password = AuthUtils.get_password_hash(password=admin_init_password)
        superuser_hash_password = AuthUtils.get_password_hash(
            password=superuser_init_password
        )
        user_hash_password = AuthUtils.get_password_hash(password=user_init_password)

        initial_users = [
            {
                "username": admin_init_login,
                "email": f"{admin_init_login}@aperam.com",
                "hashed_password": admin_hash_password,
                "user_type": UserTypeEnum.ADMIN,
            },
            {
                "username": superuser_init_login,
                "email": f"{superuser_init_login}@aperam.com",
                "hashed_password": superuser_hash_password,
                "user_type": UserTypeEnum.SUPERUSER,
            },
            {
                "username": user_init_login,
                "email": f"{user_init_login}@aperam.com",
                "hashed_password": user_hash_password,
                "user_type": UserTypeEnum.USER,
            },
        ]

        for user_data in initial_users:
            existing_user = (
                session.query(User)
                .filter(
                    or_(
                        User.username == user_data["username"],
                        User.email == user_data["email"],
                    )
                )
                .first()
            )
            if existing_user:
                continue

            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=user_data["hashed_password"],
                is_active=True,
                user_type=user_data["user_type"],
            )
            session.add(user)

        session.commit()
    finally:
        session.close()
