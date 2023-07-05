import os
import random
import pymongo
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restful import Api
from flask_pymongo import PyMongo
from marshmallow import Schema, fields, validate, validates, ValidationError

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
api = Api(app)

CORS(app)

mongo_uri = os.environ.get("MONGO_URI")

myclient = pymongo.MongoClient(mongo_uri)
mydb = myclient["cowry"]

carts = mydb["carts"]
orders = mydb["carts"]
supplier_products = mydb["supplier_products"]

current_date = datetime.now()

#######################SCHEMAS#########################
class BrandsGateway(Schema):
    product_type = fields.Str(required=True)
    group_sku = fields.Str(required=True)
    variation_type = fields.Str(required=True)
    product_sku = fields.Str(required=True)
    brand = fields.Str(required=True)
    name = fields.Str(required=True)
    retail_price = fields.Int(required=True)
    wholesale_price = fields.Int(required=True)
    description = fields.Str(required=True)
    main_picture = fields.Str(required=True)
    picture_1 = fields.Str(required=False)
    picture_2 = fields.Str(required=False)
    picture_3 = fields.Str(required=False)
    picture_4 = fields.Str(required=False)
    picture_5 = fields.Str(required=False)
    gender = fields.Str(required=True)
    category = fields.Str(required=True)
    subcategory = fields.Str(required=True)
    size = fields.Str(required=True)
    quantity = fields.Int(required=True)
    color = fields.Str(required=True)
    material = fields.Str(required=True)
    product_code = fields.Str(required=False)
    origin = fields.Str(required=True)
    product_id = fields.Int(required=True)
    size_slug = fields.Str(required=False)
    weight = fields.Str(required=True)
    location = fields.Str(required=True)
    currency = fields.Str(required=True)

class TradeEasy(Schema):
    image = fields.Str(required=True)
    article = fields.Str(required=True)
    model = fields.Str(required=True)
    size = fields.Str(required=True)
    quantity = fields.Int(required=True)
    wholesale_price = fields.Str(required=True)
    retail_price = fields.Str(required=True)
    gender = fields.Str(required=True)

class XMBO(Schema):
    image = fields.Str(required=True)
    ref = fields.Int(required=False)
    brand = fields.Str(required=True)
    ean = fields.Str(required=True)
    description = fields.Str(required=True)
    hs = fields.Str(required=False)
    material = fields.Str(required=False)
    made_in = fields.Str(required=False)
    quantity = fields.Int(required=True)
    retail_price = fields.Str(required=True)
    price = fields.Str(required=True)
    article = fields.Str(required=True)

class DNCWholesale(Schema):
    store = fields.Str(required=True)
    lot = fields.Str(required=True)
    merch_category = fields.Str(required=True)
    wholesale_quantity = fields.Str(required=True)
    wholesale_price = fields.Str(required=True)
    brand = fields.Str(required=True)
    description = fields.Str(required=True)
    color = fields.Str(required=True)
    size = fields.Str(required=True)
    quantity = fields.Int(required=True)
    retail_price = fields.Str(required=True)
    image = fields.Str(required=True)



########################APIs###########################

@app.route('/add_to_cart', methods=['POST'])
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

@app.route('/brandsgateway/add_product', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        payload = BrandsGateway().load(data)

        product_details = {"supplier_id" : "001","product_type" : payload["product_type"], "group_sku" : payload["group_sku"],
                            "variation_type" : payload["variation_type"], "product_sku" : payload["product_sku"],
                              "brand" : payload["brand"], "name" : payload["name"], "retail_price" : payload["retail_price"],
                                "wholesale_price" : payload["wholesale_price"], "description" : payload["description"],
                                  "main_picture" : payload["main_picture"], "picture_1" : payload["picture_1"],
                                    "picture_2" : payload["picture_2"], "picture_3" : payload["picture_3"],
                                      "picture_4" : payload["picture_4"], "picture_5" : payload["picture_5"], "gender" : payload["gender"],
                                        "category" : payload["category"], "subcategory" : payload["subcategory"], "size" : payload["size"],
                                          "quantity" : payload["quantity"], "color" : payload["color"], "material" : payload["material"],
                                            "product_id" : payload["product_id"], "size_slug" : payload["size_slug"], "weight" : payload["weight"],
                                              "location" : payload["location"], "currency" : payload["currency"]}

        supplier_products.insert_one(product_details)
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return jsonify({'message': 'product added successfully.'}), 200
    
@app.route('/tradeeasy/add_product', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        payload = TradeEasy().load(data)

        product_details = {"supplier_id" : "002", "image" : payload["image"], "article" : payload["article"],
                            "model" : payload["model"], "size" : payload["size"],
                              "quantity" : payload["quantity"], "price" : payload["price"], "retail_price" : payload["retail_price"], "gender" : payload["gender"]}

        supplier_products.insert_one(product_details)
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return jsonify({'message': 'product added successfully.'}), 200

@app.route('/dncwholesale/add_product', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        payload = DNCWholesale().load(data)

        product_details = {"supplier_id" : "003", "store" : payload["store"], "lot" : payload["lot"],
                            "merch_category" : payload["merch_category"], "wholesale_quantity" : payload["wholesale_quantity"],
                              "color" : payload["color"], "brand" : payload["brand"], "retail_price" : payload["retail_price"],
                                "wholesale_price" : payload["wholesale_price"], "description" : payload["description"],
                                  "size" : payload["size"], "image" : payload["image"],
                                    "quantity" : payload["quantity"]}

        supplier_products.insert_one(product_details)
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return jsonify({'message': 'product added successfully.'}), 200

@app.route('/xmbo/add_product', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        payload = XMBO().load(data)

        product_details = {"supplier_id" : "004", "image" : payload["image"], "ref" : payload["ref"],
                            "brand" : payload["brand"], "ean" : payload["ean"],
                              "hs" : payload["hs"], "material" : payload["material"], "made_in" : payload["made_in"],
                                "retail_price" : payload["retail_price"], "description" : payload["description"],
                                  "quantity" : payload["quantity"], "price" : payload["price"],
                                    "article" : payload["article"]}

        supplier_products.insert_one(product_details)
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return jsonify({'message': 'product added successfully.'}), 200

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
