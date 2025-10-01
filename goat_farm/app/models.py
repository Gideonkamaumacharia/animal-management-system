from datetime import date
from app.extensions import db

class Animal(db.Model):
    __tablename__ = "animals"

    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.String(50), unique=True, nullable=False)
    breed = db.Column(db.String(50), nullable=False)
    sex = db.Column(db.String(10), nullable=False)  # "Male" or "Female"
    birth_date = db.Column(db.Date, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    health_status = db.Column(db.String(100), default="Healthy")
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    treatments = db.relationship("Treatment", backref="animal", lazy=True)
    sale = db.relationship("Sale", backref="animal", uselist=False)

    def __repr__(self):
        return f"<Animal {self.tag_id} - {self.breed}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "tag_id": self.tag_id,
            "breed": self.breed,
            "sex": self.sex,
            "birth_date": self.birth_date,
            "weight": self.weight,
            "health_status": self.health_status,
            "notes": self.notes,
            "treatments": [t.to_dict() for t in self.treatments],
            "sale": self.sale.to_dict() if self.sale else None
        }


class Treatment(db.Model):
    __tablename__ = "treatments"

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey("animals.id"), nullable=False)
    treatment_type = db.Column(db.String(50), nullable=False)  # Vaccination, Deworming, etc.
    treatment_date = db.Column(db.Date, default=date.today)
    next_due_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Treatment {self.treatment_type} for Animal {self.animal_id}>"


class Sale(db.Model):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey("animals.id"), nullable=True)
    buyer_name = db.Column(db.String(100), nullable=False)
    sale_date = db.Column(db.Date, default=date.today)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Sale Animal {self.animal_id} - {self.price}>"


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    expense_type = db.Column(db.String(50), nullable=False)  # Feed, Vet, Staff, etc.
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, default=date.today)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Expense {self.expense_type} - {self.amount}>"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.email}>"
