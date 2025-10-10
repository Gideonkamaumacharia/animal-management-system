import pytest
from app.extensions import db
from app.models import Animal, Treatment # and other models

# The 'client' argument tells pytest to run the client() fixture from conftest.py
def test_create_sale_calculates_profit_correctly(client):
    """
    GIVEN a test client
    WHEN the '/sales/make' endpoint is posted to with correct data
    THEN check the profit is calculated correctly
    """
    # 1. Arrange: Add data to the in-memory SQLite database
    # a test should only define the absolute minimum data required to verify a specific behavior.
    animal = Animal(tag_id="TEST001", acquisition_price=15000.00, sex="Doe", breed="Saanen")
    db.session.add(animal)
    db.session.commit()

    treatment1 = Treatment(animal_id=animal.id, treatment_type="Vaccination", cost=500.00)
    treatment2 = Treatment(animal_id=animal.id, treatment_type="Deworming", cost=350.50)
    db.session.add_all([treatment1, treatment2])
    db.session.commit()

    # 2. Act: Use the client to make a request
    sale_payload = {
        "animal_id": animal.id,
        "buyer_name": "Test Buyer",
        "price": 25000.00,
        "sale_date": "2025-10-10"
    }
    response = client.post('/sales/make', json=sale_payload)

    # 3. Assert
    assert response.status_code == 201
    data = response.get_json()
    expected_profit = 9149.50
    assert data["sale"]["profit"] == pytest.approx(expected_profit)