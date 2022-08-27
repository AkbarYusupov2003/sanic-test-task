import datetime

import sqlalchemy as sa

from main import Base


class Bill(Base):
    __tablename__ = "bill"

    id = sa.Column(sa.types.INTEGER, primary_key=True)
    balance = sa.Column(sa.types.INTEGER, nullable=False)
    user_id = sa.Column(sa.ForeignKey("users.id"), nullable=False)


class Transaction(Base):
    __tablename__ = "transaction"

    id = sa.Column(sa.types.INTEGER, primary_key=True)
    deposit = sa.Column(sa.types.INTEGER, nullable=False)
    bill_id = sa.Column(sa.ForeignKey("bill.id"), nullable=False)
    created_at = sa.Column(
        sa.types.DateTime, default=datetime.datetime.now, nullable=False
    )


bill = Bill.__table__
transaction = Transaction.__table__
