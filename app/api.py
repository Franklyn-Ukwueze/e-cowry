import requests, os
import random
import pymongo
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restful import Api, Resource
from flask_pymongo import PyMongo
from functools import wraps
from marshmallow import Schema, fields, validate, validates, ValidationError
#from cryptography.fernet import Fernet


# Generate a secret key for encryption
# SECRET_KEY = Fernet.generate_key()
# cipher_suite = Fernet(SECRET_KEY)

# In-memory database to store encrypted payment information (for demonstration purposes)
#encrypted_payments = {}

# CJ Dropshipping API Base URL
CJ_API_BASE_URL = os.environ.get("CJ_API_BASE_URL")

CJ_API_KEY = os.environ.get("CJ_API_KEY")

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
api = Api(app)

CORS(app)

cowry_token = os.environ.get("COWRY_KEY")
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
def cowry_token_required(f):
    @wraps(f)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return {"status": False, "message": "Access token is missing at " + request.url, "data": None}, 401

        if token == cowry_token:
            return f(*args, **kwargs)
        else:
            return {"status": False, "message": "Invalid access token at " + request.url, "data": None}, 401

    return decorated

########################APIs###########################
class Home(Resource):
#    @urgent2k_token_required
    def get(self):
        return {'message': "Welcome to the homepage of this webservice."}
api.add_resource(Home,'/')


@app.route('/add_to_cart', methods=['POST'])
@cowry_token_required
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
@cowry_token_required
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
@cowry_token_required
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
@cowry_token_required
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
@cowry_token_required
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
@cowry_token_required
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
@cowry_token_required
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
@cowry_token_required
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
@cowry_token_required
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
@cowry_token_required
def get_supplier_products(supplier_id):
    try:
        data = supplier_products.find({"supplier_id" : int(supplier_id)},{ "_id": 0,})
        product_list = list()
        for i in data:
            product_list.append(i)
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return {"status": True, "message":"Products have been retrieved successfully", "data": product_list }, 200

@app.route('/convert_currency', methods=['POST'])
@cowry_token_required
def convert_currency():
    
    try:
        # Retrieve request data
        data = request.get_json()
        amount = data.get('amount')
        amount = float(amount)
        base_currency = data.get('base_currency')
        target_currency = data.get('target_currency')

        # Make API call to convert currency
        api_key = os.environ.get("CONVERSION_API_KEY")
        url = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={}&to_currency={}&apikey={}".format(
                base_currency, target_currency, api_key)
        response = requests.get(url)
        response = response.json()
        exchange_rate = response["Realtime Currency Exchange Rate"].get("5. Exchange Rate")
        exchange_rate = float(exchange_rate)
        
        # Check if conversion is successful
        if exchange_rate:
            conversion_rate = exchange_rate
            if conversion_rate:
                converted_amount = amount * conversion_rate
                result = {
                    'amount': amount,
                    'base_currency': base_currency,
                    'target_currency': target_currency,
                    'converted_amount': round(converted_amount, 2)
                }
    except Exception as e:
        return jsonify(message=f"An exception occurred: {e}", status=False)
    else:
        return jsonify(status=True, message=f"{base_currency} to {target_currency} successfully.", data=result ), 200



@app.route('/collect_payment', methods=['POST'])
def collect_payment():
    data = request.json

    # Assume data includes 'card_number', 'expiration_date', 'cvv', etc.
    card_number = data['card_number']
    expiration_date = data['expiration_date']
    cvv = data['cvv']

    # Encrypt payment information
    payment_info = f"{card_number}|{expiration_date}|{cvv}"
    encrypted_payment = cipher_suite.encrypt(payment_info.encode())

    # Store encrypted payment information (insecure for demonstration purposes)
    encrypted_payments[data['user_id']] = encrypted_payment

    return jsonify({"message": "Payment information collected and encrypted."})

@app.route('/get_payment/<user_id>', methods=['GET'])
def get_payment(user_id):
    if user_id in encrypted_payments:
        encrypted_payment = encrypted_payments[user_id]
        decrypted_payment_info = cipher_suite.decrypt(encrypted_payment).decode()
        card_number, expiration_date, cvv = decrypted_payment_info.split('|')
        return jsonify({
            "card_number": card_number[-4:],  # Display only the last 4 digits
            "expiration_date": expiration_date,
            "cvv": cvv[-3:],  # Display only the last 3 digits
        })
    else:
        return jsonify({"message": "Payment information not found."}), 404

# @app.route('/order/<string:order_id>/status', methods=['GET', 'PUT'])
# def order_status(order_id):
#     if request.method == 'GET':
#         order = orders.find_one({'order_id': order_id}, {'_id': 0})
#         if order:
#             return jsonify({
#                 'message': f"Order with order id {order_id} retrieved successfully",
#                 'data': order,
#                 'status': True
#             })
#         else:
#             return jsonify({
#                 'message': f"Could not find order with order id {order_id}",
#                 'data': None,
#                 'status': False
#             }), 404
#     elif request.method == 'PUT':
#         data = request.json
#         status = data.get('status')
#         stage = data.get('stage')
#         admin_email = data.get('admin-email')
#         customer_email = data.get('customer-email')

#         # The payload the client sent is incomplete 
#         if not status or not stage or not admin_email or not customer_email:
#             return jsonify({
#                 'message': 'Missing required payload',
#                 'data': None,
#                 'status': False
#             }), 400

#         # Update the order status in the database
#         update = orders.update_one({'order_id': order_id}, {
#             '$set': {
#                 'status': status,
#                 'stage': stage
#             }
#         })
#         if update.matched_count == 0:
#             return jsonify({
#                 'message': f"Could not find order with order id {order_id}",
#                 'data': None,
#                 'status': False
#             }), 404
        
#         # Send out emails to admin and customer
#         subject = f"Update to order ({order_id}) - {status}"
#         recipients = [admin_email, customer_email]
#         body = f"The order with order id {order_id} has been updated"
#         message = Message(subject=subject, recipients=recipients, body=body)
#         mail.send(message)

#         return jsonify({
#             'message': f"Order with order id {order_id} has been successfully updated",
#             'data': None,
#             'status': True
#         }), 200


# @app.route("/update/<tracking_number>", methods=["PUT"])
# def update_package_status(tracking_number):
#     new_status = request.json.get("status")
#     new_location = request.json.get("location")

#     package_info = packages_collection.find_one({"_id": tracking_number})
#     if package_info:
#         old_status = package_info["status"]

#         # Update package status and location
#         packages_collection.update_one(
#             {"_id": tracking_number},
#             {
#                 "$set": {
#                     "status": new_status,
#                     "location": new_location,
#                 },
#                 "$push": {
#                     "tracking_history": {
#                         "status": new_status,
#                         "location": new_location,
#                     },
#                 },
#             },
#         )

#         # Send emails to admin and customer
#         send_email(package_info["admin_email"], f"Package {tracking_number} Status Update", f"Status: {old_status} -> {new_status}\nLocation: {new_location}")
#         send_email(package_info["customer_email"], f"Package {tracking_number} Status Update", f"Status: {old_status} -> {new_status}\nLocation: {new_location}")

#         return jsonify({"message": "Package updated successfully"})
#     else:
#         return jsonify({"error": "Package not found"}), 404


# def send_email(to_email, subject, message):
#     # Configure your SMTP server settings
#     smtp_server = "smtp.example.com"
#     smtp_port = 587
#     smtp_username = "your_username"
#     smtp_password = "your_password"

#     # Create and send the email
#     from_email = "your_email@example.com"
#     msg = MIMEText(message)
#     msg["Subject"] = subject
#     msg["From"] = from_email
#     msg["To"] = to_email

#     try:
#         server = smtplib.SMTP(smtp_server, smtp_port)
#         server.starttls()
#         server.login(smtp_username, smtp_password)
#         server.sendmail(from_email, to_email, msg.as_string())
#         server.quit()
#         print(f"Email sent to {to_email}")
#     except Exception as e:
#         print(f"Email sending failed: {str(e)}")


# CJ Dropshipping API Base URL
CJ_API_BASE_URL = "https://api.cjdropshipping.com/app/"

CJ_API_KEY = "your_api_key"


# Endpoint to retrieve all products from cj dropshipping
@app.route("/get_cj_products", methods=["GET"])
def get_products():
    # Make a request to CJ Dropshipping's product list API
    headers = {
        "CJ-Access-Token": f"{CJ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{CJ_API_BASE_URL}product/getCategory", headers=headers)
    
    if response.status_code == 200:
        products_data = response.json()
        return jsonify(products_data)
    else:
        return jsonify({"error": "Failed to retrieve products"}), response.status_code

# Endpoint to retrieve a product's details by ID, Product SKU, or Variant SKU on CJ dropshipping
@app.route("/get_cj_product_details", methods=["GET"])
def get_product_details():
    # Get the product ID, Product SKU, or Variant SKU from the query parameters
    product_id = request.args.get("product_id")
    product_sku = request.args.get("product_sku")
    variant_sku = request.args.get("variant_sku")
    
    # Check if any of the parameters are provided
    if not (product_id or product_sku or variant_sku):
        return jsonify({"error": "Please provide product_id, product_sku, or variant_sku"}), 400

    # Construct the request URL based on the provided parameter
    if product_id:
        url = f"{CJ_API_BASE_URL}product/query?pid={product_id}"
    elif product_sku:
        url = f"{CJ_API_BASE_URL}product/query?productSku={product_sku}"
    elif variant_sku:
        url = f"{CJ_API_BASE_URL}product/query?variantSku={variant_sku}"

    # Make a request to CJ Dropshipping's product details API
    headers = {
        "CJ-Access-Token": f"{CJ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        product_data = response.json()
        return jsonify(product_data)
    else:
        return jsonify({"error": "Failed to retrieve product details"}), response.status_code


# Endpoint to create an order on cj dropshipping
@app.route("/create_order", methods=["POST"])
def create_order():
    # Extract data from the request
    data = request.json

    # Check if required parameters are provided
    required_params = [
        "orderNumber",
        "shippingCountryCode",
        "shippingCountry",
        "shippingProvince",
        "shippingCity",
        "shippingAddress",
        "shippingAddress2",
        "shippingCustomerName",
        "shippingZip",
        "shippingPhone",
        "logisticName",
        "fromCountryCode",
        "products",
        "vid",
        "quantity",
        "shippingName",
    ]

    for param in required_params:
        if param not in data:
            return jsonify({"error": f"Missing required parameter: {param}"}), 400

    # Optional parameters
    remark = data.get("remark")
    houseNumber = data.get("houseNumber")
    email = data.get("email")

    # Construct the request URL
    url = f"{CJ_API_BASE_URL}shopping/order/createOrder"

    # Construct the order data
    order_data = {
        "orderNumber": data["orderNumber"],
        "shippingCountryCode": data["shippingCountryCode"],
        "shippingCountry": data["shippingCountry"],
        "shippingProvince": data["shippingProvince"],
        "shippingCity": data["shippingCity"],
        "shippingAddress": data["shippingAddress"],
        "shippingAddress2": data["shippingAddress2"],
        "shippingCustomerName": data["shippingCustomerName"],
        "shippingZip": data["shippingZip"],
        "shippingPhone": data["shippingPhone"],
        "logisticName": data["logisticName"],
        "fromCountryCode": data["fromCountryCode"],
        "products": data["products"],
        "vid": data["vid"],
        "quantity": data["quantity"],
        "shippingName": data["shippingName"],
    }

    # Add optional parameters if provided
    if remark:
        order_data["remark"] = remark
    if houseNumber:
        order_data["houseNumber"] = houseNumber
    if email:
        order_data["email"] = email

    # Make a POST request to CJ Dropshipping's create order API
    headers = {
        "Authorization": f"{CJ_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=order_data, headers=headers)

    if response.status_code == 200:
        order_response = response.json()
        return jsonify(order_response)
    else:
        return jsonify({"error": "Failed to create the order"}), response.status_code
    
if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
