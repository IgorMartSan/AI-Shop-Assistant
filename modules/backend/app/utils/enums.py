# Criando o Enum corretamente
from enum import Enum

class UserTypeEnum(str, Enum):
    ADMIN = "admin"
    USER = "user"
    SUPERUSER = "superuser"