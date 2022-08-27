import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from main import Base


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.types.INTEGER, primary_key=True)
    username = sa.Column(sa.types.String(64), unique=True, nullable=False)
    hashed_password = sa.Column(sa.types.String(256), nullable=False)
    is_active = sa.Column(sa.types.Boolean, server_default="f", nullable=False)
    is_admin = sa.Column(sa.types.Boolean, server_default="f", nullable=False)


class UserVerification(Base):
    __tablename__ = "user_verification"

    uuid = sa.Column(UUID(as_uuid=True), primary_key=True)
    user_id = sa.Column(sa.ForeignKey("users.id"), nullable=False)

    __table_args__ = (
        sa.UniqueConstraint("user_id", "uuid", name="_fk_user_uuid_uc"),
    )


users = User.__table__
user_verification = UserVerification.__table__
