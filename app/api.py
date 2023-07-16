import requests, os
import random
import pymongo
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restful import Api
from flask_pymongo import PyMongo
from functools import wraps
from marshmallow import Schema, fields, validate, validates, ValidationError

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
api = Api(app)

CORS(app)

urgent2k_token = os.environ.get("URGENT_2K_KEY")
mongo_uri = os.environ.get("MONGO_URI")

myclient = pymongo.MongoClient(mongo_uri)
mydb = myclient["cowry"]

carts = mydb["carts"]
orders = mydb["carts"]
supplier_products = mydb["supplier_products"]
suppliers = mydb["suppliers"]

current_date = datetime.now()

#######################SCHEMAS#########################
class RegisterSupplier(Schema):
    supplier_name = fields.Str(required=True)
    location = fields.Str(required=False)
    contact_address = fields.Str(required=False)
    email = fields.Str(required=True)
    phone = fields.Str(required=False)

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
    description_plain = fields.Str(required=True)
    main_picture = fields.Str(required=True)
    other_pictures = fields.List(fields.Dict(), required=False)
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
    other_pictures = fields.List(fields.Dict(), required=False)
    article = fields.Str(required=True)
    model = fields.Str(required=True)
    category = fields.Str(required=True)
    size = fields.Str(required=True)
    quantity = fields.Int(required=True)
    wholesale_price = fields.Str(required=True)
    retail_price = fields.Str(required=True)
    gender = fields.Str(required=True)
    currency = fields.Str(required=True)

class XMBO(Schema):
    image = fields.Str(required=True)
    other_pictures = fields.List(fields.Dict(), required=False)
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
    currency = fields.Str(required=True)

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
    other_pictures = fields.List(fields.Dict(), required=False)
    currency = fields.Str(required=True)

# decorator function frequesting api key as header
def urgent2k_token_required(f):
    @wraps(f)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return {"status": False, "message": "Access token is missing at " + request.url, "data": None}, 401

        if token == urgent2k_token:
            return f(*args, **kwargs)
        else:
            return {"status": False, "message": "Invalid access token at " + request.url, "data": None}, 401

    return decorated

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
@urgent2k_token_required
def brandsgateway_add_product():
    try:
        data = request.get_json()
        payload = BrandsGateway().load(data)

        product_details = {"supplier_id" : 1,"product_type" : payload["product_type"], "group_sku" : payload["group_sku"],
                            "variation_type" : payload["variation_type"], "product_sku" : payload["product_sku"],
                              "brand" : payload["brand"], "name" : payload["name"], "retail_price" : payload["retail_price"],
                                "wholesale_price" : payload["wholesale_price"], "description" : payload["description"], "description_plain" : payload["description_plain"],
                                  "main_picture" : payload["main_picture"], "other_pictures" : payload["other_pictures"], "gender" : payload["gender"],
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
@urgent2k_token_required
def tradeeasy_add_product():
    try:
        data = request.get_json()
        payload = TradeEasy().load(data)

        product_details = {"supplier_id" : 2, "image" : payload["image"], "article" : payload["article"],
                            "model" : payload["model"],  "category" : payload["category"], "size" : payload["size"],
                              "quantity" : payload["quantity"], "price" : payload["price"], "retail_price" : payload["retail_price"], "gender" : payload["gender"],
                               "other_pictures" : payload["other_pictures"], "currency" : payload["currency"]}

        supplier_products.insert_one(product_details)
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return jsonify({'message': 'product added successfully.'}), 200

@app.route('/dncwholesale/add_product', methods=['POST'])
@urgent2k_token_required
def dncwholesale_add_product():
    try:
        data = request.get_json()
        payload = DNCWholesale().load(data)

        product_details = {"supplier_id" : 3, "store" : payload["store"], "lot" : payload["lot"],
                            "merch_category" : payload["merch_category"], "wholesale_quantity" : payload["wholesale_quantity"],
                              "color" : payload["color"], "brand" : payload["brand"], "retail_price" : payload["retail_price"],
                                "wholesale_price" : payload["wholesale_price"], "description" : payload["description"],
                                  "size" : payload["size"], "image" : payload["image"],
                                   "other_pictures" : payload["other_pictures"],
                                    "quantity" : payload["quantity"], "currency" : payload["currency"]}

        supplier_products.insert_one(product_details)
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return jsonify({'message': 'product added successfully.'}), 200

@app.route('/xmbo/add_product', methods=['POST'])
@urgent2k_token_required
def xmbo_add_product():
    try:
        data = request.get_json()
        payload = XMBO().load(data)

        product_details = {"supplier_id" : 4, "image" : payload["image"], "ref" : payload["ref"],
                            "brand" : payload["brand"], "ean" : payload["ean"], "other_pictures" : payload["other_pictures"],
                              "hs" : payload["hs"], "material" : payload["material"], "made_in" : payload["made_in"],
                                "retail_price" : payload["retail_price"], "description" : payload["description"],
                                  "quantity" : payload["quantity"], "price" : payload["price"],
                                    "article" : payload["article"], "currency" : payload["currency"]}

        supplier_products.insert_one(product_details)
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return jsonify({'message': 'product added successfully.'}), 200
    
@app.route('/get/products', methods=['GET', 'POST'])
@urgent2k_token_required
def get_products():
    try:
        data = supplier_products.find({},{ "_id": 0})
        product_list = list()
        for i in data:
            product_list.append(i)
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return {"status": True, "message":"Products have been retrieved successfully", "data": product_list }, 200

@app.route('/supplier/register', methods=['POST'])
@urgent2k_token_required
def register_supplier():
    try:
        data = request.get_json()
        payload = RegisterSupplier().load(data)

        # Find the maximum supplier ID
        max_supplier_id = suppliers.find_one(sort=[("supplier_id", -1)])
        if max_supplier_id:
            supplier_id = max_supplier_id['supplier_id'] + 1
        else:
            supplier_id = 1

        supplier_details = {"supplier_id" : supplier_id, "supplier_name" : payload["supplier_name"],
                        "location" : payload["location"], "contact_address" : payload["contact_address"],
                         "email" : payload["email"], "phone" : payload["phone"] }
        
        suppliers.insert_one(supplier_details)
        
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return {"status": True, "message": f"{payload['supplier_name']} has been registered with supplier ID {supplier_id}", "data":supplier_id}, 200

@app.route('/get/suppliers', methods=['GET', 'POST'])
@urgent2k_token_required
def get_suppliers():
    try:
        data = suppliers.find({},{ "_id": 0})
        supplier_list = list()
        for i in data:
            supplier_list.append(i)
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return {"status": True, "message":"Suppliers have been retrieved successfully", "data": supplier_list }, 200

@app.route('/get/<string:supplier_id>/products', methods=['GET', 'POST'])
@urgent2k_token_required
def get_products(supplier_id):
    try:
        data = supplier_products.find({"supplier_id" : int(supplier_id)},{ "_id": 0,})
        product_list = list()
        for i in data:
            product_list.append(i)
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return {"status": True, "message":"Products have been retrieved successfully", "data": product_list }, 200

@app.route('/convert', methods=['POST'])
def convert_currency():
    
    try:
        # Retrieve request data
        data = request.get_json()
        amount = data.get('amount')
        base_currency = data.get('base_currency')
        target_currency = data.get('target_currency')

        # Make API call to convert currency
        api_key = os.environ.get("CONVERSION_API_KEY")
        url = f"https://v6.exchangeratesapi.io/latest?access_key={api_key}&base={base_currency}&symbols={target_currency}"
        response = requests.get(url)
        exchange_rates = response.json().get('rates')
        
        # Check if conversion is successful
        if exchange_rates:
            conversion_rate = exchange_rates.get(target_currency)
            if conversion_rate:
                converted_amount = amount * conversion_rate
                result = {
                    'amount': amount,
                    'base_currency': base_currency,
                    'target_currency': target_currency,
                    'converted_amount': converted_amount
                }
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return {"status": True, "message":"{base_currency} to {target_currency} successfully.", "data": result }, 200

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
