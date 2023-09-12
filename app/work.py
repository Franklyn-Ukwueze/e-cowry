import os
#import PyPDF2
#import tabula
import requests
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

# def read_excel_and_send_to_api(excel_file_path, api_url):
#     # Read data from the Excel file into a pandas DataFrame
#     df = pd.read_excel(excel_file_path)

#     # Loop through each row of the DataFrame
#     for index, row in df.iterrows():
#         # Convert the row data to a dictionary (you can modify this based on your Excel structure)
#         data = row.to_dict()

#         try:
#             # Send the data to the API using the POST request
#             response = requests.post(api_url, json=data)

#             # Check if the API call was successful (HTTP status code 200-299)
#             if response.status_code >= 200 and response.status_code < 300:
#                 print(f"Row {index+1}: Data sent successfully to the API.")
#             else:
#                 print(f"Row {index+1}: Failed to send data to the API. Status Code: {response.status_code}")
#                 print(response.text)  # Optionally, print the error message from the API
#         except requests.exceptions.RequestException as e:
#             print(f"Row {index+1}: An error occurred while sending data to the API: {e}")

# # Provide the path to your Excel file and the API URL
# excel_file_path = "path/to/your/excel_file.xlsx"
# api_url = "https://example.com/api/endpoint"

# read_excel_and_send_to_api(excel_file_path, api_url)


# def read_pdf_data(pdf_file):
#     data = []
#     with open(pdf_file, 'rb') as file:
#         pdf_reader = PyPDF2.PdfFileReader(file)
#         num_pages = pdf_reader.numPages

#         for page_number in range(num_pages):
#             page = pdf_reader.getPage(page_number)
#             text = page.extract_text()
#             lines = text.split('\n')

#             for line in lines:
#                 # Assuming that each row is separated by tabs or spaces
#                 row_data = line.split('\t')  # Replace '\t' with ' ' if separated by spaces
#                 data.append(row_data)

#     return data

# def send_data_to_api(api_url, data):
#     for row_data in data:
#         # Assuming your API expects a JSON payload
#         payload = {'data': row_data}

#         # Send the data to the API
#         response = requests.post(api_url, json=payload)

#         # You can process the API response here if needed
#         if response.status_code == 200:
#             print("Data sent successfully!")
#         else:
#             print(f"Failed to send data. Status code: {response.status_code}")

# pdf_file_path = "path/to/your/pdf_file.pdf"
# api_url = "https://example.com/api/endpoint"  # Replace this with your API endpoint URL

# data = read_pdf_data(pdf_file_path)
# send_data_to_api(api_url, data)


# def convert_pdf_to_excel(pdf_file, excel_file):
#     # Read tables from the PDF file
#     tables = tabula.read_pdf(pdf_file, pages='all', multiple_tables=True)

#     # Assuming all tables are relevant, concatenate them into a single DataFrame
#     df = pd.concat(tables)

#     # Save the DataFrame to an Excel file
#     df.to_excel(excel_file, index=False)
#     print(f"PDF data successfully converted to {excel_file}.")

# @app.route("/track/<tracking_number>", methods=["GET"])
# def track_package(tracking_number):
#     package_info = packages_collection.find_one({"_id": tracking_number})
#     if package_info:
#         return jsonify(package_info)
#     else:
#         return jsonify({"error": "Package not found"}), 404


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

def get_api_response(url, request_type, payload=None):
    headers = {"content-type": "application/json"}

    try:
        #Make API call
        if request_type == "get":
            r = requests.get(url=url, headers=headers, json=payload)
        elif request_type == "post":
            r = requests.post(url=url, headers=headers, json=payload)
        elif request_type == "put":
            r = requests.put(url=url, headers=headers, json=payload)

            
        print(f"Status code: {r.status_code}")  #Print status code
        response = r.json()

        
    except Exception as e:
        return f"Encountered error: {e}"

    return response

#if __name__ == "__main__":
    # pdf_file_path = "path/to/your/pdf_file.pdf"
    # excel_file_path = "path/to/your/excel_file.xlsx"

    # convert_pdf_to_excel(pdf_file_path, excel_file_path)
payload = {}

print(get_api_response("https://developers.cjdropshipping.com/api2.0/v1/authentication/getAccessToken", "post", payload))