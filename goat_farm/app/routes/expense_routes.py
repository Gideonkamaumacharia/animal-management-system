from flask import Blueprint, jsonify, request
from app.models import Sale, Animal, Expense
from datetime import datetime,timedelta,date
from app.extensions import db
from sqlalchemy import func

expense_bp = Blueprint("expenses", __name__, url_prefix="/expenses")

@expense_bp.route("/get", methods=["GET"])
def get_expenses():
    expenses = Expense.query.all()
    return jsonify([expense.to_dict() for expense in expenses]), 200

@expense_bp.route("/<int:expense_id>", methods=["GET"])
def get_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)

    if not expense:
        return jsonify({"message": "Expense not found"}), 404
    return jsonify(expense.to_dict()), 200

@expense_bp.route("/total", methods=["GET"])
def get_total_expenses():
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    total_last_30_days = (
        db.session.query(func.sum(Expense.amount))
        .filter(Expense.date >= thirty_days_ago)
        .scalar()
    ) or 0  

    total_all_time = db.session.query(func.sum(Expense.amount)).scalar() or 0

    return jsonify({
        "total_expenses_last_30_days": total_last_30_days,
        "total_expenses_all_time": total_all_time
    }), 200


@expense_bp.route("/<int:expense_id>/update", methods=["PATCH"])
def update_expense(expense_id):
    data = request.get_json()
    expense = Expense.query.get_or_404(expense_id)
    expense.amount = data.get("amount", expense.amount)
    expense.description = data.get("description", expense.description)
    expense.date = date.fromisoformat(data["date"]) if "date" in data else expense.date
    db.session.commit()
    return jsonify(expense.to_dict()), 200

@expense_bp.route("/<int:expense_id>/delete", methods=["DELETE"])
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    return jsonify({"message": "Expense deleted successfully"}), 200