from flask import Blueprint, jsonify, request
from app.models import Sale, Animal
from datetime import date
from app.extensions import db

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
    data = request.json
    new_sale = Sale(
        animal_id=data["animal_id"],
        buyer_name=data["buyer_name"],
        buyer_contact=data["buyer_contact"],
        sale_date=data["sale_date"],
        price=data["price"],
        payment_method=data["payment_method"],
        payment_received=data["payment_received"],
        purpose=data["purpose"],
        notes=data["notes"]
    )
    db.session.add(new_sale)
    db.session.commit()
    return jsonify(new_sale.to_dict()), 201

@sales_bp.route("/<int:sale_id>", methods=["PATCH"])
def update_sale(sale_id):   
    data = request.json
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

@sales_bp.route("/<int:sale_id>", methods=["DELETE"])
def delete_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    db.session.delete(sale)
    db.session.commit()
    return jsonify({"message": "Sale deleted successfully"}), 200   

@sales_bp.route("/animal/<int:animal_id>", methods=["GET"])
def get_sales_by_animal(animal_id):
    sales = Sale.query.filter_by(animal_id=animal_id).all()
    return jsonify([sale.to_dict() for sale in sales]), 200 

@sales_bp.route("/animal/<int:animal_id>/total", methods=["GET"])
def get_total_sales_by_animal(animal_id):   
    total_sales = db.session.query(db.func.sum(Sale.price)).filter_by(animal_id=animal_id).scalar() or 0.0
    return jsonify({"animal_id": animal_id, "total_sales": total_sales}), 200   

@sales_bp.route("/total", methods=["GET"])
def get_total_sales():
    total_sales = db.session.query(db.func.sum(Sale.price)).scalar() or 0.0
    return jsonify({"total_sales": total_sales}), 200   

@sales_bp.route("/recent", methods=["GET"])
def get_recent_sales():
    recent_sales = Sale.query.order_by(Sale.sale_date.desc()).limit(5).all()
    return jsonify([sale.to_dict() for sale in recent_sales]), 200      

@sales_bp.route("/animal/<int:animal_id>/mark_as_sold", methods=["POST"])
def mark_animal_as_sold(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    if animal.status == "sold":
        return jsonify({"message": "Animal is already marked as sold"}), 400
    animal.status = "sold"
    db.session.commit()
    return jsonify({"message": f"Animal {animal_id} marked as sold"}), 200  

@sales_bp.route("/animal/<int:animal_id>/mark_as_available", methods=["POST"])
def mark_animal_as_available(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    if animal.status == "active":
        return jsonify({"message": "Animal is already marked as available"}), 400
    animal.status = "active"
    db.session.commit()
    return jsonify({"message": f"Animal {animal_id} marked as available"}), 200 

@sales_bp.route("/stats/daily", methods=["GET"])
def get_daily_sales_stats():    
    daily_stats = db.session.query(
        Sale.sale_date,
        db.func.count(Sale.id).label("total_sales"),
        db.func.sum(Sale.price).label("total_revenue")
    ).group_by(Sale.sale_date).all()
    
    result = [
        {
            "sale_date": stat.sale_date.isoformat() if stat.sale_date else None,
            "total_sales": stat.total_sales,
            "total_revenue": stat.total_revenue
        }
        for stat in daily_stats
    ]
    return jsonify(result), 200 

@sales_bp.route("/stats/monthly", methods=["GET"])
def get_monthly_sales_stats():  
    monthly_stats = db.session.query(
        db.func.strftime("%Y-%m", Sale.sale_date).label("sale_month"),
        db.func.count(Sale.id).label("total_sales"),
        db.func.sum(Sale.price).label("total_revenue")
    ).group_by("sale_month").all()
    
    result = [
        {
            "sale_month": stat.sale_month,
            "total_sales": stat.total_sales,
            "total_revenue": stat.total_revenue
        }
        for stat in monthly_stats
    ]
    return jsonify(result), 200     

@sales_bp.route("/stats/yearly", methods=["GET"])
def get_yearly_sales_stats():   
    yearly_stats = db.session.query(
        db.func.strftime("%Y", Sale.sale_date).label("sale_year"),
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

