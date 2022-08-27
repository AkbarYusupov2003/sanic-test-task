import sqlalchemy as sa

from main import Base


class Product(Base):
    __tablename__ = "product"

    id = sa.Column(sa.types.INTEGER, primary_key=True)
    title = sa.Column(sa.types.String(64), nullable=False)
    description = sa.Column(sa.types.Text, nullable=False)
    price = sa.Column(sa.types.INTEGER, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
        }


product = Product.__table__
