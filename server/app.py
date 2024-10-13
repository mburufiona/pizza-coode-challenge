#!/usr/bin/env python3

from server.models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    restaurant_list = [
        {'id': r.id, 'name': r.name, 'address': r.address} for r in restaurants
    ]
    return jsonify(restaurant_list),200

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        pizzas = [{'id': rp.pizza.id, 'name': rp.pizza.name, 'ingredients': rp.pizza.ingredients, 'price': rp.price} for rp in restaurant.restaurant_pizzas]
        return jsonify({'id': restaurant.id, 'name': restaurant.name, 'address': restaurant.address, 'restaurant_pizzas': pizzas}), 200
    else:
        return jsonify({'error': 'Restaurant not found'}), 404

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return jsonify({'message': 'Restaurant deleted successfully'}), 204
    else:
        return jsonify({'error': 'Restaurant not found'}), 404
    
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizza_list = [
        {'id': p.id, 'name': p.name, 'ingredients': p.ingredients} for p in pizzas
    ]
    return jsonify(pizza_list), 200
@app.route('/restaurant_pizzas', methods=['POST'])
def add_restaurant_pizza():
    data = request.get_json()
    restaurant_id = data.get('restaurant_id')
    pizza_id = data.get('pizza_id')
    price = data.get('price')

    if restaurant_id is None or pizza_id is None or price is None:
        return jsonify({'errors': ['Missing required fields']}), 400
    
    if price < 1 or price > 30:
        return jsonify({'errors': ['validation errors']}), 400

    restaurant = Restaurant.query.get(restaurant_id)
    pizza = Pizza.query.get(pizza_id)

    if not restaurant or not pizza:
        return jsonify({'errors': ['Invalid restaurant or pizza ID']}), 404

    restaurant_pizza = RestaurantPizza(restaurant_id=restaurant_id, pizza_id=pizza_id, price=price)
    db.session.add(restaurant_pizza)
    db.session.commit()

    return make_response(jsonify({'message': 'Restaurant pizza added successfully', 'id': restaurant_pizza.id, 'price': restaurant_pizza.price, 'pizza_id': restaurant_pizza.pizza_id, 'restaurant_id': restaurant_pizza.restaurant_id, 'pizza': {
        'id': pizza.id, 'name': pizza.name, 'ingredients': pizza.ingredients
    }, 'restaurant': {'id': restaurant.id, 'name': restaurant.name, 'address': restaurant.address}
    }), 201)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
