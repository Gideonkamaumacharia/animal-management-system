from flask import Blueprint, request, jsonify
from app.models import db, Animal, Breeding
from datetime import date, timedelta

breeding_bp = Blueprint("breeding", __name__, url_prefix="/breeding")

@breeding_bp.route("/add", methods=["POST"])
def add_breeding_record():
    data = request.get_json()
    doe_id = data.get("doe_id")
    buck_id = data.get("buck_id")
    mating_date_str = data.get("mating_date") # Expecting "YYYY-MM-DD"

    # --- Validation ---
    if not all([doe_id, buck_id, mating_date_str]):
        return jsonify({"error": "doe_id, buck_id, and mating_date are required."}), 400

    doe = Animal.query.get(doe_id)
    buck = Animal.query.get(buck_id)

    if not doe or not buck:
        return jsonify({"error": "One or both animals not found."}), 404
    
    if doe.sex.lower() != 'doe':
        return jsonify({"error": f"Animal {doe.tag_id} is not a Doe."}), 400
        
    if buck.sex.lower() != 'buck':
        return jsonify({"error": f"Animal {buck.tag_id} is not a Buck."}), 400

    # --- Logic ---
    try:
        mating_date = date.fromisoformat(mating_date_str)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

    # Goats have a gestation period of approximately 150 days
    expected_kidding_date = mating_date + timedelta(days=150)

    new_breeding_record = Breeding(
        doe_id=doe_id,
        buck_id=buck_id,
        mating_date=mating_date,
        expected_kidding_date=expected_kidding_date,
        status="Confirmed" # Start with a confirmed status
    )

    db.session.add(new_breeding_record)
    db.session.commit()

    return jsonify({
        "message": "Breeding record created successfully.",
        "record": new_breeding_record.to_dict()
    }), 201