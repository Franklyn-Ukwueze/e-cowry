import os
import random
import pymongo
from datetime import datetime
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

app = Flask(__name__)

mongo_uri = os.environ.get("MONGO_URI")

myclient = pymongo.MongoClient(mongo_uri)
mydb = myclient["cowry"]

carts = mydb["carts"]
orders = mydb["carts"]

current_date = datetime.now()

@app.route('/api/add-to-cart', methods=['POST'])
def add_to_cart():
    try:
        # Retrieve user account information from request
        user_id = request.json.get('user_id')
        # Get the item details from the request body
        product_id = request.json.get('product_id')
        quantity = request.json.get('quantity')

        if not user_id or not product_id:
            return jsonify({'error': 'Invalid request. Please provide user_id and product_id.'}), 400
        
        cart = carts.find_one({}, {f"{user_id}" : True})

        # Check if the user has an existing cart
        if not cart:
            new_cart = {f"{user_id}" : True, "items": [{"product_id" : f"{product_id}", "quantitiy": quantity} ]}
            carts.insert_one(new_cart)

        elif cart:
            filter = {f"{user_id}" : True}
            new_items = [{"product_id" : f"{product_id}", "quantitiy": quantity}]
            update = {"$push": {"items":{"$each": new_items}}}

            # Update the record in the collection
            carts.update_one(filter, update)

        

    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return jsonify({'message': 'Item added to cart successfully.'}), 200

@app.route('/submit_order', methods=['POST'])
def submit_order():
    # Get the order details from the request
    user_id = request.json.get("user_id")
    items = request.json.get("items")
    total_cost = request.json.get("total_cost")

    order_id = str(random.randint(100000000000, 999999999999))
    data = orders.find_one({}, {"order_id": order_id})

    while data:
        order_id = random.randint(100000000000, 999999999999)

    order_data = {"user_id" : f"{user_id}", "order_id" : f"{order_id}", "date" : current_date, "items" : items, "total_cost" : total_cost}

    orders.insert_one(order_data)

    response = {
        'status': 'success',
        'message': 'Order submitted successfully!'
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
