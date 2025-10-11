from flask import Blueprint, jsonify, request
from app.models import Sale, Animal
from datetime import date,datetime,timedelta
from app.extensions import db
from app.models import Expense
from sqlalchemy import func,case

sales_bp = Blueprint("sales", __name__, url_prefix="/sales")    

@sales_bp.route("/", methods=["GET"])
def get_sales():
    sales = Sale.query.all()
    return jsonify([sale.to_dict() for sale in sales])

@sales_bp.route("/<int:sale_id>", methods=["GET"])
def get_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    return jsonify(sale.to_dict())

@sales_bp.route("/make", methods=["POST"])
def create_sale():
    data = request.get_json()

    animal_id = data.get("animal_id")
    buyer_name = data.get("buyer_name")
    buyer_contact = data.get("buyer_contact")
    sale_date = date.fromisoformat(data["sale_date"]) if "sale_date" in data else None
    price = data.get("price")
    payment_method = data.get("payment_method")
    payment_received = data.get("payment_received", True)
    receipt_number = data.get("receipt_number")
    purpose = data.get("purpose")
    status = data.get("status", "Active")
    notes = data.get("notes")

    animal = Animal.query.get(animal_id)
    if not animal:
        return jsonify({"error": "Animal not found"}), 404

    if animal.status == "Sold":
        return jsonify({"error": "Animal already sold"}), 400
    
    total_expenses = db.session.query(db.func.sum(Expense.amount)).filter_by(animal_id=animal.id).scalar() or 0

    acquisition_price = animal.acquisition_price or 0.0
    profit = price - (acquisition_price + total_expenses)

    sale = Sale(
        animal_id=animal_id,
        buyer_name=buyer_name,
        buyer_contact=buyer_contact,
        sale_date=sale_date,
        price=price,
        payment_method=payment_method,
        payment_received=payment_received,
        receipt_number=receipt_number,
        purpose=purpose,
        status=status,
        profit=profit,
        notes=notes
    )

    animal.status = "Sold"

    db.session.add(sale)
    db.session.commit()

    return jsonify({"message": "Sale created successfully", "sale": sale.to_dict()}), 201

@sales_bp.route("/total_profit", methods=["GET"])
def get_total_profit():
    last_thirty_days = datetime.utcnow() - timedelta(days=30)
    profit_for_the_last_30_days = db.session.query(
        db.func.sum(Sale.profit)
    ).filter(Sale.sale_date >= last_thirty_days).scalar() or 0.0

    annual_profit = db.session.query(
        db.func.sum(Sale.profit)
    ).filter(Sale.sale_date >= datetime(datetime.utcnow().year, 1, 1)).scalar() or 0.0

    total_profit = db.session.query(
        db.func.sum(Sale.profit)
    ).scalar() or 0.0

    return jsonify(
        {
            "total_profit": profit_for_the_last_30_days,
            "annual_profit": annual_profit,
            "lifetime_profit": total_profit
        }), 200

# A list of recent sales.

@sales_bp.route("/recent", methods=["GET"])
def get_recent_sales():

    recent_sales = Sale.query.order_by(Sale.sale_date.desc()).limit(2).all()
    return jsonify([sale.to_dict() for sale in recent_sales]), 200

@sales_bp.route("/<int:sale_id>", methods=["PATCH"])
def update_sale(sale_id):
    data = request.get_json()
    sale = Sale.query.get_or_404(sale_id)
    sale.animal_id = data.get("animal_id", sale.animal_id)
    sale.buyer_name = data.get("buyer_name", sale.buyer_name)
    sale.buyer_contact = data.get("buyer_contact", sale.buyer_contact)
    sale.sale_date = date.fromisoformat(data["sale_date"]) if "sale_date" in data else sale.sale_date
    sale.price = data.get("price", sale.price)
    sale.payment_method = data.get("payment_method", sale.payment_method)
    sale.payment_received = data.get("payment_received", sale.payment_received)
    sale.purpose = data.get("purpose", sale.purpose)
    sale.status = data.get("status", sale.status)
    sale.notes = data.get("notes", sale.notes)
    db.session.commit()
    return jsonify(sale.to_dict()), 200

 
@sales_bp.route("/stats/daily", methods=["GET"])
def get_daily_sales_stats():
    # Perform a LEFT JOIN between Sale and Expense tables
    daily_stats = (
        db.session.query(
            Sale.sale_date.label("sale_date"),
            func.count(Sale.id).label("total_sales"),
            func.sum(Sale.price).label("total_revenue"),
            func.coalesce(func.sum(Expense.amount), 0).label("total_expenses"),
            (
                func.sum(Sale.price) - func.coalesce(func.sum(Expense.amount), 0)
            ).label("total_profit")
        )
        .outerjoin(Expense, Sale.animal_id == Expense.animal_id)
        .group_by(Sale.sale_date)
        .order_by(Sale.sale_date.desc())
        .all()
    )

    result = [
        {
            "sale_date": stat.sale_date.isoformat(),
            "total_sales": stat.total_sales,
            "total_revenue": stat.total_revenue,
            "total_expenses": stat.total_expenses,
            "total_profit": stat.total_profit
        }
        for stat in daily_stats
    ]

    return jsonify(result), 200

from sqlalchemy import func, and_
from flask import jsonify

@sales_bp.route("/stats/monthly", methods=["GET"])
def get_monthly_sales_stats():
    # 1) Build a per-sale aggregation: sale price + sum of expenses for that animal up to the sale date
    per_sale = (
        db.session.query(
            Sale.id.label("sale_id"),
            Sale.animal_id.label("animal_id"),
            Sale.sale_date.label("sale_date"),
            Sale.price.label("sale_price"),
            func.coalesce(func.sum(Expense.amount), 0).label("total_expenses")
        )
        .outerjoin(
            Expense,
            and_(
                Expense.animal_id == Sale.animal_id,
                Expense.date <= Sale.sale_date
            )
        )
        .group_by(Sale.id)  
    ).subquery()
    #THis is exactly what the above subquery does:
    """
    SELECT * FROM (
    SELECT Sale.id, Sale.price, SUM(Expense.amount) AS total_expenses
    FROM Sale LEFT JOIN Expense ...
    GROUP BY Sale.id
) AS per_sale
    """

    # 2) Aggregate per-sale rows into monthly stats
    monthly_stats = (
        db.session.query(
            func.to_char(per_sale.c.sale_date, "YYYY-MM").label("sale_month"),
            func.count(per_sale.c.sale_id).label("total_sales"),
            func.sum(per_sale.c.sale_price).label("total_revenue"),
            func.sum(per_sale.c.total_expenses).label("total_expenses"),
            (func.sum(per_sale.c.sale_price) - func.sum(per_sale.c.total_expenses)).label("total_profit")
        )
        .group_by("sale_month")
        .order_by("sale_month")
        .all()
    )

    result = [
        {
            "sale_month": stat.sale_month,
            "total_sales": stat.total_sales,
            "total_revenue": float(stat.total_revenue or 0),
            "total_expenses": float(stat.total_expenses or 0),
            "total_profit": float(stat.total_profit or 0)
        }
        for stat in monthly_stats
    ]

    return jsonify(result), 200


@sales_bp.route("/stats/yearly", methods=["GET"])
def get_yearly_sales_stats():   
    yearly_stats = db.session.query(
        db.func.to_char(Sale.sale_date, "YYYY").label("sale_year"),
        db.func.count(Sale.id).label("total_sales"),
        db.func.sum(Sale.price).label("total_revenue")
    ).group_by("sale_year").all()
    
    result = [
        {
            "sale_year": stat.sale_year,
            "total_sales": stat.total_sales,
            "total_revenue": stat.total_revenue
        }
        for stat in yearly_stats
    ]
    return jsonify(result), 200     

@sales_bp.route("/stats/payment_method", methods=["GET"])
def get_sales_stats_by_payment_method():    
    payment_method_stats = db.session.query(
        Sale.payment_method,
        db.func.count(Sale.id).label("total_sales"),
        db.func.sum(Sale.price).label("total_revenue")
    ).group_by(Sale.payment_method).all()
    
    result = [
        {
            "payment_method": stat.payment_method,
            "total_sales": stat.total_sales,
            "total_revenue": stat.total_revenue
        }
        for stat in payment_method_stats
    ]
    return jsonify(result), 200     

@sales_bp.route("/stats/purpose", methods=["GET"])
def get_sales_stats_by_purpose():       
    purpose_stats = db.session.query(
        Sale.purpose,
        db.func.count(Sale.id).label("total_sales"),
        db.func.sum(Sale.price).label("total_revenue")
    ).group_by(Sale.purpose).all()
    
    result = [
        {
            "purpose": stat.purpose,
            "total_sales": stat.total_sales,
            "total_revenue": stat.total_revenue
        }
        for stat in purpose_stats
    ]
    return jsonify(result), 200 

@sales_bp.route("/stats/status", methods=["GET"])
def get_sales_stats_by_status():        
    status_stats = db.session.query(
        Sale.status,
        db.func.count(Sale.id).label("total_sales"),
        db.func.sum(Sale.price).label("total_revenue")
    ).group_by(Sale.status).all()
    
    result = [
        {
            "status": stat.status,
            "total_sales": stat.total_sales,
            "total_revenue": stat.total_revenue
        }
        for stat in status_stats
    ]
    return jsonify(result), 200

@sales_bp.route("/search", methods=["GET"])
def search_sales():                 
    query_params = request.args
    filters = []
    
    if "buyer_name" in query_params:
        filters.append(Sale.buyer_name.ilike(f"%{query_params['buyer_name']}%"))
    if "payment_method" in query_params:
        filters.append(Sale.payment_method == query_params["payment_method"])
    if "purpose" in query_params:
        filters.append(Sale.purpose == query_params["purpose"])
    if "status" in query_params:
        filters.append(Sale.status == query_params["status"])
    if "min_price" in query_params:
        filters.append(Sale.price >= float(query_params["min_price"]))
    if "max_price" in query_params:
        filters.append(Sale.price <= float(query_params["max_price"]))
    if "start_date" in query_params:
        filters.append(Sale.sale_date >= date.fromisoformat(query_params["start_date"]))
    if "end_date" in query_params:
        filters.append(Sale.sale_date <= date.fromisoformat(query_params["end_date"]))
    
    sales = Sale.query.filter(*filters).all()
    return jsonify([sale.to_dict() for sale in sales]), 200

# @sales_bp.route("/<int:sale_id>", methods=["DELETE"])
# def delete_sale(sale_id):
#     sale = Sale.query.get_or_404(sale_id)
#     db.session.delete(sale)
#     db.session.commit()
#     return jsonify({"message": "Sale deleted successfully"}), 200   

# @sales_bp.route("/animal/<int:animal_id>", methods=["GET"])
# def get_sales_by_animal(animal_id):
#     sales = Sale.query.filter_by(animal_id=animal_id).all()
#     return jsonify([sale.to_dict() for sale in sales]), 200 

# @sales_bp.route("/animal/<int:animal_id>/total", methods=["GET"])
# def get_total_sales_by_animal(animal_id):   
#     total_sales = db.session.query(db.func.sum(Sale.price)).filter_by(animal_id=animal_id).scalar() or 0.0
#     return jsonify({"animal_id": animal_id, "total_sales": total_sales}), 200  