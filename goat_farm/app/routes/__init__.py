from .routes import main
from .animal_routes import animals_bp
from .treatment_routes import treatments_bp
from .sales_routes import sales_bp
from .expense_routes import expense_bp

# Keep a list of all blueprints here
all_blueprints = [main, animals_bp, treatments_bp, sales_bp, expense_bp]
