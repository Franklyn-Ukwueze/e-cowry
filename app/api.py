import os
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

app = Flask(__name__)

mongo_uri = os.environ.get("MONGO_URI")
mongo = PyMongo(app, uri=mongo_uri)

# Placeholder for user accounts and their respective carts
carts = mongo.db.carts.find()


@app.route('/api/add-to-cart', methods=['POST'])
def add_to_cart():
    # Retrieve user account information from request
    user_id = request.json.get('user_id')
     # Get the item details from the request body
    item = request.json.get('item')
    quantity = request.json.get('quantity')

    if not user_id or not item:
        return jsonify({'error': 'Invalid request. Please provide user_id and item_id.'}), 400
    
    # Check if the user has an existing cart
    if user_id not in carts:
        carts[user_id] = []
    
   
    # Add the item to the user's cart
    carts[user_id].append({'item': item, 'quantity': quantity})

    
    return jsonify({'message': 'Item added to cart successfully.'}), 200


if __name__ == '__main__':
    app.run()
