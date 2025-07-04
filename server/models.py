from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# Naming convention for Alembic migrations
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


# Restaurant Model

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # Relationships
    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        backref="restaurant",
        cascade="all, delete-orphan"
    )
    pizzas = association_proxy("restaurant_pizzas", "pizza")

    # Serialization
    serialize_rules = ('-restaurant_pizzas.restaurant',)

    def __repr__(self):
        return f"<Restaurant {self.name}>"



# Pizza Model

class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    # Relationships
    restaurant_pizzas = db.relationship("RestaurantPizza", backref="pizza")
    restaurants = association_proxy("restaurant_pizzas", "restaurant")

    # Serialization: remove restaurant_pizzas from output
    serialize_rules = ('-restaurant_pizzas',)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


# RestaurantPizza Join Model

class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)

    # Serialization
    serialize_rules = (
        '-pizza.restaurant_pizzas',
        '-restaurant.restaurant_pizzas',
    )

    # Validation for price
    @validates("price")
    def validate_price(self, key, value):
        if not (1 <= value <= 30):
            raise ValueError("Price must be between 1 and 30.")
        return value

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
