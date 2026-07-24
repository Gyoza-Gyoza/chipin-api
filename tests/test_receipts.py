from fastapi.testclient import TestClient
from decimal import Decimal

from main import app

def test_create_receipt(test_receipt):
    client = TestClient(app)
    response = client.post(
        "/receipts",
        json = test_receipt.model_dump(mode = "json"))
    assert response.status_code == 201

def test_get_receipt_by_id(created_receipt):
    client = TestClient(app)
    response = client.get(f"/receipts/{created_receipt['receipt_id']}")
    total_cost = Decimal(0.0)
    for item in created_receipt['items']:
        total_cost += Decimal(item['amount'])
    receipt_dict = response.json()

    assert response.status_code == 200
    assert receipt_dict['receipt_id'] == created_receipt['receipt_id']
    assert receipt_dict['title'] == created_receipt['title']
    # assert receipt_dict['amount'] == str(total_cost)
    assert receipt_dict['items'] == created_receipt['items']

def test_get_receipt_by_user(created_receipt):
    client = TestClient(app)

    response = client.get(f"/receipts/users/{created_receipt['owner_id']}")
    receipt_dict = response.json()

    assert response.status_code == 200
    assert isinstance(receipt_dict, list)
    for receipt in receipt_dict:
        assert receipt['owner_id'] == created_receipt['owner_id']

def test_update_receipt(created_receipt, test_receipt_update):
    client = TestClient(app)

    # Get receipt and ensures it's okay
    response = client.get(f"/receipts/{created_receipt['receipt_id']}")

    assert response.status_code == 200
    initial_receipt = response.json()
    # Checks initial value of variables that are going to be updated
    assert initial_receipt['title'] == created_receipt['title']
    assert initial_receipt['items'] == created_receipt['items']

    # Update receipt
    updated_receipt_dict = test_receipt_update.model_dump(mode = "json")
    update = client.put(
        f"/receipts/{created_receipt['receipt_id']}",
        json = updated_receipt_dict)
    assert update.status_code == 200

    # Get and check post update value
    updated_dict = client.get(f"/receipts/{created_receipt['receipt_id']}").json()
    assert updated_dict['title'] == test_receipt_update.title
    assert updated_dict['items'] == updated_receipt_dict['items']
    assert updated_dict['owner_id'] == initial_receipt['owner_id']

def test_delete_receipt(created_receipt):
    client = TestClient(app)

    response = client.delete(f"/receipts/{created_receipt['receipt_id']}")
    assert response.status_code == 204

    check = client.get(f"/receipts/{created_receipt['receipt_id']}")
    assert check.status_code == 404