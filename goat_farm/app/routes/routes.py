from flask import Blueprint, jsonify

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return jsonify({"message": "Goat Farm Management System is running!"})

# Additional routes can be added here for managing animals, treatments, sales, and expenses.
