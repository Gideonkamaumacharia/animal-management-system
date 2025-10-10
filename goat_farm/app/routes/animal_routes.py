from flask import Blueprint, jsonify, request
from app.models import Animal
from datetime import date
from app.extensions import db

animals_bp = Blueprint("animal", __name__, url_prefix="/animals")

@animals_bp.route("/get", methods=["GET"])
def get_animals():
    animals = Animal.query.filter(Animal.status == "Active").all()
    return jsonify([animal.to_dict() for animal in animals]), 200


@animals_bp.route("/<int:animal_id>", methods=["GET"])
def get_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    if animal.status != "Active":
        return jsonify({"message": "Animal is not active"}), 404
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
        notes=data.get("notes", ""),
        category=data.get("category", ""),
        image_url=data.get("image_url", ""),
        status = data.get("status", "Active"),
        acquisition_date=date.fromisoformat(data["acquisition_date"]) if "acquisition_date" in data else None,
        acquisition_price=data.get("acquisition_price"),
        source=data.get("source"),
        offspring_count= data.get("offspring_count", 0),
        mother_id=data.get("mother_id"),
        father_id=data.get("father_id"),
        created_at=data.get("created_at"),
        updated_at=data.get("updated_at")   
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
    animal.category = data.get("category", animal.category)
    animal.image_url = data.get("image_url", animal.image_url)
    animal.status = data.get("status", animal.status)
    animal.mother_id = data.get("mother_id", animal.mother_id)
    animal.father_id = data.get("father_id", animal.father_id)
    animal.updated_at = data.get("updated_at", animal.updated_at)   

    db.session.commit()
    return jsonify(animal.to_dict(), {"message": "Animal updated successfully"}), 200

# This route is for handling archiving (soft delete)
@animals_bp.route("/archive", methods=["GET"])
def get_archived_animals():
    status_filter = request.args.get("status") #means that if status is provided in the query params(url), we filter by it
    query = Animal.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    animals = query.all()
    return jsonify([animal.to_dict() for animal in animals]), 200

@animals_bp.route("/deceased", methods=["GET"])
def get_deceased_animals():
    status_filter = request.args.get("status")

    if status_filter:
        animals = Animal.query.filter_by(status=status_filter).all()
    else:
        # Default: show only active animals
        animals = Animal.query.filter(Animal.status != "Deceased").all()

    return jsonify([animal.to_dict() for animal in animals]), 200

@animals_bp.route("/total/animals", methods=["GET"])
def get_total_animals():
    total = Animal.query.count()

    category_counts = db.session.query(Animal.category, db.func.count(Animal.id)).group_by(Animal.category).all()
    category_summary = {category or "uncategorized": count for category, count in category_counts}
    
    return jsonify({"total_animals": total, "category_summary": category_summary}), 200