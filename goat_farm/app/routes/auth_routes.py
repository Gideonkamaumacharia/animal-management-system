# app/routes/auth_routes.py
from flask import Blueprint, request, jsonify
from app.models import User
from app.extensions import db, bcrypt
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    is_admin = data.get("is_admin", False)
    password = data.get("password")

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    if not all([name, email, password]):
        return jsonify({"error": "Name, email, and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email address already in use"}), 409

    new_user = User(name=name, email=email, is_admin=is_admin,password=password_hash)
    

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User {name} created successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password") 

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        
        additional_claims = {"is_admin": user.is_admin}
        
        access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
        
        return jsonify(access_token=access_token)

    return jsonify({"error": "Invalid credentials"}), 401
   