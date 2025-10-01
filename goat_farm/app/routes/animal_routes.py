from flask import Blueprint, jsonify, request
from app.models import Animal
from datetime import date
from app.extensions import db

animals_bp = Blueprint("animal", __name__, url_prefix="/animals")

@animals_bp.route("/get", methods=["GET"])
def get_animals():
    animals = Animal.query.all()
    return jsonify([animal.to_dict() for animal in animals]), 200

@animals_bp.route("/<int:animal_id>", methods=["GET"])
def get_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    return jsonify(animal.to_dict()), 200

@animals_bp.route("/add", methods=["POST"])
def add_animal():
    data = request.get_json()
    new_animal = Animal(
        tag_id=data["tag_id"],
        breed=data["breed"],
        sex=data["sex"],
        birth_date=date.fromisoformat(data["birth_date"]) if "birth_date" in data else None,
        weight=data["weight"],
        health_status=data["health_status"],
        notes=data.get("notes", "")
    )
    db.session.add(new_animal)
    db.session.commit()
    return jsonify(new_animal.to_dict(), {"message": "Animal added successfully"}), 201

@animals_bp.route("/<int:animal_id>/update", methods=["PATCH"])
def update_animal(animal_id):
    data = request.get_json()
    animal = Animal.query.get_or_404(animal_id)
    animal.tag_id = data.get("tag_id", animal.tag_id)
    animal.breed = data.get("breed", animal.breed)
    animal.sex = data.get("sex", animal.sex)
    animal.birth_date = date.fromisoformat(data["birth_date"]) if "birth_date" in data else animal.birth_date
    animal.weight = data.get("weight", animal.weight)
    animal.health_status = data.get("health_status", animal.health_status)
    animal.notes = data.get("notes", animal.notes)

    db.session.commit()
    return jsonify(animal.to_dict(), {"message": "Animal updated successfully"}), 200


@animals_bp.route("/<int:animal_id>/delete", methods=["DELETE"])
def delete_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    db.session.delete(animal)
    db.session.commit()
    return jsonify({"message": "Animal deleted successfully"}), 204 