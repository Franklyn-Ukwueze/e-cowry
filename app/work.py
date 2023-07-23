import os
import pandas as pd
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

def read_excel_and_send_to_api(excel_file_path, api_url):
    # Read data from the Excel file into a pandas DataFrame
    df = pd.read_excel(excel_file_path)

    # Loop through each row of the DataFrame
    for index, row in df.iterrows():
        # Convert the row data to a dictionary (you can modify this based on your Excel structure)
        data = row.to_dict()

        try:
            # Send the data to the API using the POST request
            response = requests.post(api_url, json=data)

            # Check if the API call was successful (HTTP status code 200-299)
            if response.status_code >= 200 and response.status_code < 300:
                print(f"Row {index+1}: Data sent successfully to the API.")
            else:
                print(f"Row {index+1}: Failed to send data to the API. Status Code: {response.status_code}")
                print(response.text)  # Optionally, print the error message from the API
        except requests.exceptions.RequestException as e:
            print(f"Row {index+1}: An error occurred while sending data to the API: {e}")

# Provide the path to your Excel file and the API URL
excel_file_path = "path/to/your/excel_file.xlsx"
api_url = "https://example.com/api/endpoint"

read_excel_and_send_to_api(excel_file_path, api_url)


print(add_to_cart("1234", "2223333", 2))