from flask import Blueprint, jsonify, request
from app.models import Treatment
from app.extensions import db
from datetime import date   

treatments_bp = Blueprint("treatments", __name__, url_prefix="/treatments")

ALLOWED_TREATMENT_TYPES = [
    "Vaccination",
    "Deworming",
    "Antibiotic",
    "Check-up",
    "Surgery",
    "Vitamin Supplement",
    "Other"
]



@treatments_bp.route("/get", methods=["GET"])
def get_treatments():
    treatments = Treatment.query.all()
    return jsonify([treatment.to_dict() for treatment in treatments]), 200  

@treatments_bp.route("/<int:treatment_id>", methods=["GET"])
def get_treatment(treatment_id):
    treatment = Treatment.query.get_or_404(treatment_id)
    return jsonify(treatment.to_dict()), 200    


@treatments_bp.route("/add", methods=["POST"])
def add_treatment():
    data = request.get_json()

    treatment_type = data.get("treatment_type")
    medication = data.get("medication")
    dosage = data.get("dosage")

    if not treatment_type:
        return jsonify({"error": "Treatment type is required"}), 400

    if treatment_type not in ALLOWED_TREATMENT_TYPES:
        return jsonify({"error": f"Invalid treatment type. Allowed: {ALLOWED_TREATMENT_TYPES}"}), 400

    # If "Other", require a custom description (extra field)
    if treatment_type == "Other":
        custom_type = data.get("custom_type")
        if not custom_type:
            return jsonify({"error": "Custom treatment type is required when 'Other' is selected"}), 400
        treatment_type = custom_type  # save the custom one

    treatment = Treatment(
        animal_id=data.get("animal_id"),
        treatment_type=treatment_type,
        medication=medication,
        dosage=dosage,
        treatment_date=data.get("treatment_date"),
        next_due_date=data.get("next_due_date"),
        notes=data.get("notes")
        # user_id=data.get("user_id"),
    )

    db.session.add(treatment)
    db.session.commit()

    return jsonify({"message": "Treatment added successfully"}), 201

@treatments_bp.route("/<int:treatment_id>/update", methods=["PATCH"])
def update_treatment(treatment_id):         
    data = request.get_json()
    treatment = Treatment.query.get_or_404(treatment_id)
    treatment.animal_id = data.get("animal_id", treatment.animal_id)
    treatment.treatment_type = data.get("treatment_type", treatment.treatment_type)
    treatment.treatment_date = date.fromisoformat(data["treatment_date"]) if "treatment_date" in data else treatment.treatment_date
    treatment.medication = data.get("medication", treatment.medication)
    treatment.dosage = data.get("dosage", treatment.dosage)
    treatment.next_due_date = date.fromisoformat(data["next_due_date"]) if "next_due_date" in data else treatment.next_due_date
    treatment.notes = data.get("notes", treatment.notes)
    # treatment.user_id = data.get("user_id", treatment.user_id)  

    db.session.commit()
    return jsonify(treatment.to_dict(), {"message": "Treatment updated successfully"}), 200

@treatments_bp.route("/<int:treatment_id>/delete", methods=["DELETE"])
def delete_treatment(treatment_id):
    treatment = Treatment.query.get_or_404(treatment_id)
    db.session.delete(treatment)
    db.session.commit()
    return jsonify({"message": "Treatment deleted successfully"}), 200      
