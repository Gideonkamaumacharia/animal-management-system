from datetime import date
from app.extensions import db
from sqlalchemy import event

class Animal(db.Model):
    __tablename__ = "animals"

    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.String(50), unique=True, nullable=False)
    breed = db.Column(db.String(50), nullable=False)
    sex = db.Column(db.String(10), nullable=False)  
    birth_date = db.Column(db.Date, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    health_status = db.Column(db.String(100), default="Healthy")
    notes = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)  # Kid, Doe, Buck,dairy, meat, breeding, etc.
    image_url = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    status= db.Column(db.String(20), default="Active")  # Active, Sold, Deceased, etc.
    acquisition_date = db.Column(db.Date, nullable=True)
    acquisition_price = db.Column(db.Float, nullable=True)
    source = db.Column(db.String(100), nullable=True) 
    # milk_yield = db.Column(db.Float, nullable=True)  # liters per day (latest or average)
    offspring_count = db.Column(db.Integer, default=0)

    mother_id = db.Column(db.Integer, db.ForeignKey("animals.id"), nullable=True)
    father_id = db.Column(db.Integer, db.ForeignKey("animals.id"), nullable=True)

    mother = db.relationship("Animal", remote_side=[id], foreign_keys=[mother_id], backref="offspring", lazy=True)
    father = db.relationship("Animal", remote_side=[id], foreign_keys=[father_id], backref="sired", lazy=True)

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = date.today()
        delta = today - self.birth_date

       
        if delta.days < 30:
            return f"{delta.days} day(s)"
        elif delta.days < 365:
            months = delta.days // 30
            return f"{months} month(s)"
        else:
            years = delta.days // 365
            return f"{years} year(s)"

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
            "age": self.age,
            "birth_date": self.birth_date,
            "weight": self.weight,
            "health_status": self.health_status,
            "notes": self.notes,
            "category": self.category,
            "image_url": self.image_url,
            "status": self.status,
            "mother_id": self.mother_id,
            "father_id": self.father_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,  
            "treatments": [t.to_dict() for t in self.treatments],
            "sale": self.sale.to_dict() if self.sale else None,
            "acquisition_date": self.acquisition_date,
            "acquisition_price": self.acquisition_price,
            "source": self.source,
            "offspring_count": len(self.offspring) if self.offspring else 0
        }


class Treatment(db.Model):
    __tablename__ = "treatments"

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey("animals.id"), nullable=False)
    treatment_type = db.Column(db.String(50), nullable=False)  
    treatment_date = db.Column(db.Date, default=date.today)
    medication = db.Column(db.String(100), nullable=True)
    dosage = db.Column(db.String(50), nullable=True)
    next_due_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)  #Extra details, context, instructions
    outcome = db.Column(db.String(100), nullable=True)  # e.g. Recovered, Ongoing, etc.
    cost = db.Column(db.Float, nullable=True)


    # user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # user = db.relationship("User", backref="treatments", lazy=True)

    # animals = db.relationship("Animal", backref="treatments", lazy=True)

    def __repr__(self):
        return f"<Treatment {self.treatment_type} for Animal {self.animal_id}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "animal_id": self.animal_id,
            "treatment_type": self.treatment_type,
            "treatment_date": self.treatment_date,
            "medication": self.medication,
            "dosage": self.dosage,  
            "next_due_date": self.next_due_date,
            "notes": self.notes,
            "outcome": self.outcome,
            "cost": self.cost,
            #"treated_by": self.user_id
        }
class Sale(db.Model):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey("animals.id"), unique=True, nullable=False)  # one-to-one
    buyer_name = db.Column(db.String(100), nullable=False)
    buyer_contact = db.Column(db.String(100), nullable=True)
    sale_date = db.Column(db.Date, default=date.today, nullable=False)
    price = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=True)  # e.g. Mpesa, Bank, Cash
    payment_received = db.Column(db.Boolean, default=True)  # handle partial/pending payments
    receipt_number = db.Column(db.String(50), unique=True, nullable=True)
    purpose = db.Column(db.String(50), nullable=True)  # breeding, meat, dairy, etc.
    status = db.Column(db.String(20), default="completed")  # completed, pending, cancelled
    profit = db.Column(db.Float, nullable=True)  # Sale price - acquisition price
    notes = db.Column(db.Text, nullable=True)


    #user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f"<Sale Animal {self.animal_id} - {self.price}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "animal_id": self.animal_id,
            "buyer_name": self.buyer_name,
            "buyer_contact": self.buyer_contact,
            "sale_date": self.sale_date.isoformat() if self.sale_date else None,
            "price": self.price,
            "payment_method": self.payment_method,
            "payment_received": self.payment_received,
            "receipt_number": self.receipt_number,
            "purpose": self.purpose,
            "status": self.status,
            "notes": self.notes,
            "profit": self.profit,
            #"user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
# Automatically generate a receipt number after a sale is inserted
@event.listens_for(Sale, "after_insert")
def generate_receipt(mapper, connection, target):
    receipt = f"RCPT-{target.id:05d}"
    connection.execute(
        Sale.__table__.update()
        .where(Sale.id == target.id)
            .values(receipt_number=receipt)
        )




class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    expense_type = db.Column(db.String(50), nullable=False)  # Feed, Vet, Staff, etc.
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, default=date.today)
    notes = db.Column(db.Text, nullable=True)

     # Link expense to a specific animal (optional)
    animal_id = db.Column(db.Integer, db.ForeignKey("animals.id"), nullable=True)
    animal = db.relationship("Animal", backref="expenses", lazy=True)

    # Optional: track which user/admin logged the expense
    # user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f"<Expense {self.expense_type} - {self.amount}>"
    
    @event.listens_for(Treatment, "after_insert")
    def add_treatment_expense(mapper, connection, target):
        if target.cost and target.cost > 0:
            connection.execute(
                Expense.__table__.insert().values(
                    expense_type="Treatment",
                    amount=target.cost,
                    date=target.treatment_date,
                    animal_id=target.animal_id,
                    notes=f"{target.treatment_type} ({target.medication})"
                )   
            )


    def to_dict(self):
        return {
            "id": self.id,
            "expense_type": self.expense_type,
            "amount": self.amount,
            "date": self.date,
            "notes": self.notes,
            "animal_id": self.animal_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    # created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    # updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  


    def __repr__(self):
        return f"<User {self.email}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_admin": self.is_admin
        }
