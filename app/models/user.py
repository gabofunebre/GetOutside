import enum
from sqlalchemy import Column, Integer, String, Enum as PgEnum
from app.core.db import Base


class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    VENDEDOR = "VENDEDOR"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(
        PgEnum(UserRole, name="userrole", native_enum=True),
        nullable=False,
        default=UserRole.VENDEDOR,
    )
    oauth_provider = Column(String, nullable=True)
