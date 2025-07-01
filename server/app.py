from flask import Flask, request
from flask_restful import Api, Resource
from flask_migrate import Migrate
from models import db, Restaurant, Pizza, RestaurantPizza

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True  #  Show error messages in the browser

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)


#  GET /restaurants
class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [r.to_dict() for r in restaurants], 200


#  GET /restaurants/<id> and DELETE /restaurants/<id>
class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return restaurant.to_dict(), 200
        return {"error": "Restaurant not found"}, 404

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return {}, 204
        return {"error": "Restaurant not found"}, 404


#  GET /pizzas
class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [p.to_dict() for p in pizzas], 200


#  POST /restaurant_pizzas
class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        try:
            price = data["price"]
            pizza_id = data["pizza_id"]
            restaurant_id = data["restaurant_id"]

            # Validation
            if not (1 <= price <= 30):
                raise ValueError("Price must be between 1 and 30.")

            rp = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id
            )
            db.session.add(rp)
            db.session.commit()

            return rp.to_dict(), 201

        except Exception as e:
            return {"errors": [str(e)]}, 400


#  Register API routes
api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantById, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")


#  Optional root route
@app.route('/')
def home():
    return "<h1>Pizza Restaurants API</h1>"


#  Run server
if __name__ == '__main__':
    app.run(port=5555)
