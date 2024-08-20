from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import time
from bson.objectid import ObjectId
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the Flask application
app = Flask(__name__)

# MongoDB connection string
CONNECTION_STRING = "mongodb://localhost:27017/"

# Create a MongoDB client
client = MongoClient(CONNECTION_STRING)

# Database and collection names
DB_NAME = "Work"
COLLECTION_NAME = "data"

# Get database and collection
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

@app.route('/')
def index():
    return render_template('index.html')

# Create a document
@app.route('/create', methods=['POST'])
def create():
    name = request.form.get('name')
    age = request.form.get('age')
    city = request.form.get('city')
    document = {"name": name, "age": int(age), "city": city}

    try:
        collection.insert_one(document)
        logging.info("Document created successfully: %s", document)
        return jsonify({"message": "Document created successfully!"}), 201
    except Exception as e:
        logging.error("Error creating document: %s", e)
        return jsonify({"message": "An error occurred while creating the document."}), 500

# Read documents
@app.route('/read', methods=['GET'])
def read():
    start_time = time.time()  # Start timing

    try:
        documents = list(collection.find().limit(1))  # Read only one document
        for doc in documents:
            doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
        end_time = time.time()  # End timing
        time_taken = end_time - start_time  # Calculate time taken

        logging.info("Document read successfully in %s seconds", time_taken)
        return jsonify({"documents": documents, "time_taken": time_taken}), 200
    except Exception as e:
        logging.error("Error reading document: %s", e)
        return jsonify({"message": "An error occurred while reading documents."}), 500

# Update a document
@app.route('/update/<id>', methods=['PUT'])
def update(id):
    data = request.json
    new_age = data.get('new_age')
    query = {"_id": ObjectId(id)}
    new_values = {"$set": {"age": int(new_age)}}

    try:
        result = collection.update_one(query, new_values)
        if result.matched_count:
            logging.info("Document updated successfully for query: %s", query)
            return jsonify({"message": "Document updated successfully!"}), 200
        else:
            logging.warning("No document found for query: %s", query)
            return jsonify({"message": "No document found to update."}), 404
    except Exception as e:
        logging.error("Error updating document: %s", e)
        return jsonify({"message": "An error occurred while updating the document."}), 500

# Delete a document
@app.route('/delete/<id>', methods=['DELETE'])
def delete(id):
    query = {"_id": ObjectId(id)}

    try:
        result = collection.delete_one(query)
        if result.deleted_count:
            logging.info("Document deleted successfully for query: %s", query)
            return jsonify({"message": "Document deleted successfully!"}), 200
        else:
            logging.warning("No document found for query: %s", query)
            return jsonify({"message": "No document found to delete."}), 404
    except Exception as e:
        logging.error("Error deleting document: %s", e)
        return jsonify({"message": "An error occurred while deleting the document."}), 500

if __name__ == '__main__':
    app.run(debug=True)
