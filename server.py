from flask import Flask, render_template, render_template_string, request, jsonify, send_from_directory,redirect, url_for
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
import os
import re
import spacy
from bson import json_util
from word2number import w2n
from werkzeug.utils import secure_filename
from bson import json_util,ObjectId
app = Flask(__name__)

CORS(app, supports_credentials=True)


# Load the English model
nlp = spacy.load("en_core_web_sm")

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["Documents"]
collection = db["storage"]
users_collection = db["users"] 
doubts_collection = db["doubts"]

# Folder to store doubt images
# ..
current_user_id = None 
# Folder to store doubt images
DOUBT_IMAGES_FOLDER = "AllDoubts"
app.config["DOUBT_IMAGES_FOLDER"] = DOUBT_IMAGES_FOLDER

# Create the folder if it doesn't exist
os.makedirs(DOUBT_IMAGES_FOLDER, exist_ok=True)
# Route to handle login
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    user_class = data.get("class")

    # Validate input
    if not username or not password or not user_class:
        return jsonify(error="Please fill in all the fields"), 400

    # Check if the username is already taken (you may need to adjust this based on your data model)
    if users_collection.find_one({"username": username}):
        return jsonify(error="Username already exists. Please choose a different username."), 400

    # Create a new user record (replace this with your MongoDB insertion logic)
    new_user = {
        "username": username,
        "password": password,
        "class": user_class,
    }
    result = users_collection.insert_one(new_user)

    if result.inserted_id:
        # Redirect to the login page after successful registration
        return jsonify(message="Registration successful", redirect=url_for('login'))
    else:
        return jsonify(error="Registration failed. Please try again."), 500
    
    
@app.route('/login', methods=['POST'])
def login():
    global current_user_id  # Use the global keyword to modify the global variable
    data = request.json
    username = data.get("username")
    password = data.get("password")

    # Replace this with the actual MongoDB query to fetch user data
    user_data = users_collection.find_one({"username": username, "password": password})

    if user_data:
        current_user_id = str(user_data["_id"])
        return jsonify(message="Login successful", user_class=user_data.get("class"))
    else:
        return jsonify(error="Invalid credentials")

# Route to handle logout
@app.route('/logout', methods=['POST'])
def logout():
    global current_user_id
    current_user_id = None  # Clear the current user ID on logout
    return jsonify(message="Logout successful")
@app.route('/checkAuth', methods=['GET'])
def check_auth():
    user_id = current_user_id

    if user_id:
        return jsonify(authenticated=True, user_id=user_id)
    else:
        return jsonify(authenticated=False)

def allowed_file(filename):
    # Check if the file extension is allowed
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
  # This variable will store the currently logged-in user's ID

# ...



@app.route('/allDoubts', methods=['GET'])
def get_all_doubts():
    doubts = list(db.doubts.find({}, {'_id': 1, 'user': 1, 'class': 1, 'subject': 1, 'description': 1, 'file_type': 1}))

    # Convert ObjectId to string for JSON serialization
    for doubt in doubts:
        doubt['_id'] = str(doubt['_id'])

    return jsonify(doubts)


@app.route('/submitDoubt', methods=['POST'])
def submit_doubt():
    data = request.form
    user = data.get("user")
    class_name = data.get("class")
    subject = data.get("subject")
    description = data.get("description")

    # Save doubt image to folder
    if 'image' in request.files:
        image = request.files['image']
        if image and allowed_file(image.filename):
            # Generate a secure filename
            filename = secure_filename(image.filename)
            # Get the _id and type from the database
            # (Assuming you have a unique identifier for each doubt and its file type in the database)
            # For example, you might have a doubts_collection with fields "_id" and "file_type"
            doubt_data = {
                "user": user,
                "class": class_name,
                "subject": subject,
                "description": description,
                "file_type": filename.rsplit('.', 1)[1].lower()  # Get the file type from the filename
            }
            result = doubts_collection.insert_one(doubt_data)
            # Rename and save the image with the generated filename
            image_path = os.path.join(DOUBT_IMAGES_FOLDER, f"{str(result.inserted_id)}.{doubt_data['file_type']}")
            image.save(image_path)
            return jsonify(message="Doubt submitted successfully")
        else:
            return jsonify(error="Invalid file format")
    else:
        return jsonify(error="Image not provided")

# Serve uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config["DOUBT_IMAGES_FOLDER"], filename)

def preprocess_keyword(keyword):
    # Remove non-alphanumeric characters and convert to lowercase
    cleaned_keyword = re.sub(r'\W+', '', keyword).lower()

    # Handle variations like "7th" or "6th" only if they are at the end
    cleaned_keyword = re.sub(r'(\d+)(st|nd|rd|th)$', r'\1', cleaned_keyword)

    return cleaned_keyword

def search_documents(keywords):
    # Preprocess keywords
    processed_keywords = [preprocess_keyword(keyword) for keyword in keywords]
    user_data = users_collection.find_one({"_id": ObjectId(current_user_id)})
    user_class = user_data.get("class") if user_data else None
    print(user_class,type(user_class))
    # Build a query to search for documents
    query = {"subject": {"$in": processed_keywords}}
    if user_class:
        query["class"] = user_class

    # Check if "textbook" is in keywords
    if "textbook" in processed_keywords:
        query["rtype"] = "textbook"

    # Check if "chapter" is in keywords
    if "chapter" in processed_keywords:
        query["chapter"] = {"$in": processed_keywords}
    elif "chapters" in processed_keywords:
        query["chapter"] = {"$in": processed_keywords}
    # Perform the search
    result = collection.find(query)

    # Return the search results
    return list(result)

def replace_and_convert_number_words(text):
    def convert_number_words(word):
        # Handle special cases
        if word == "first":
            return "1st"
        elif word == "second":
            return "2nd"
        elif word == "third":
            return "3rd"
        elif word.endswith("th") and word[:-2].isdigit():
            # Handle cases like "10th", "20th", etc.
            return word[:-2]

        # Use word2number library for general cases
        try:
            return str(w2n.word_to_num(word))
        except ValueError:
            return word

    # Split the text into individual words
    words = re.findall(r'\b\w+\b', text)

    # Replace number words with their numerical equivalents
    updated_words = [convert_number_words(word.lower()) for word in words]

    # Join the words back into a string
    updated_text = ' '.join(updated_words)

    return updated_text


from bson import json_util

from bson import json_util

@app.route('/getResources', methods=['GET'])
def get_resources():
    print("request recieved")
    class_number = str(request.args.get('class'))
    subject = str(request.args.get('subject'))

    # Build a query to retrieve resources based on class and subject
    query = {"class": class_number, "subject": subject}

    # Retrieve resources from the collection
    resources = collection.find(query, {'_id': 1, 'name': 1, 'filepath': 1})

    # Convert ObjectId to string for JSON serialization
    resources_list = list(resources)
    for resource in resources_list:
        resource['_id'] = str(resource['_id'])

    # Create a new list with only 'name' and 'filepath' attributes
    results = [{'name': resource['name'], 'filepath': resource['filepath']} for resource in resources_list]

    print("Received request for class:", class_number, "and subject:", subject)
    print("Sending back the following results:", results)

    return jsonify(results=json_util.dumps(results))




@app.route('/extractKeywords', methods=['POST'])
@cross_origin(supports_credentials=True)
 # Import the library for word to number conversion
def extract_keywords():
    data = request.get_json()
    text = data.get("text")

    if text:
        # Replace and convert number words in the text before processing
        text = replace_and_convert_number_words(text)
        
        doc = nlp(text)
        unwanted_tags = ["VERB", "AUX", "ADV", "CCONJ", "ADP", "PRON"]

        keywords = [token.text for token in doc if token.pos_ not in unwanted_tags and not token.is_stop and not token.is_punct and not token.is_space]
        print(keywords)
        # Call the search_documents function to get the results
        results_list = search_documents(keywords)

        # Convert ObjectId to string for JSON serialization
        results_list = json_util.dumps(results_list)

        return jsonify(results=results_list)
    else:
        return jsonify(error="Invalid request")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
