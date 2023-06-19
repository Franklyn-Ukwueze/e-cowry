import os
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

import pymongo
mongo_uri = os.environ.get("MONGO_URI")
myclient = pymongo.MongoClient(mongo_uri)
mydb = myclient["cowry"]

mycol = mydb["carts"]

def add_to_cart(user_id, product_id, quantity):
    try:
        # Retrieve user account information from request
        #user_id = request.json.get('user_id')
        # Get the item details from the request body
        #product_id = request.json.get('product_id')
        #quantity = request.json.get('quantity')

        if not user_id or not product_id:
            return {'error': 'Invalid request. Please provide user_id and product_id.'}
        
        cart = mycol.find_one({}, {f"{user_id}" : True})

        # Check if the user has an existing cart
        if not cart:
            new_cart = {f"{user_id}" : True, "items": [{"product_id" : f"{product_id}", "quantitiy": quantity} ]}
            mycol.insert_one(new_cart)

        elif cart:
            filter = {f"{user_id}" : True}
            new_items = [{"product_id" : f"{product_id}", "quantitiy": quantity}]
            update = {"$push": {"items":{"$each": new_items}}}

            # Update the record in the collection
            mycol.update_one(filter, update)

            
        # Add the item to the user's cart
        

    except Exception as e:
        return f"An exception occurred: {e}"
    else:
        return {'message': 'Item added to cart successfully.'}

print(add_to_cart("1234", "2223333", 2))