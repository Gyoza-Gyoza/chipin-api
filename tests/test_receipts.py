from fastapi.testclient import TestClient
from main import app

def test_create_receipt(test_receipt):
    client = TestClient(app)
    response = client.post(
        "/receipts",
        json = test_receipt.model_dump(mode = "json"))
    assert response.status_code == 201

def test_get_receipt(created_receipt, test_receipt_data):
    client = TestClient(app)
    response = client.get(f"/receipts/{created_receipt['receipt_id']}")

    test_receipt_json = test_receipt_data.model_dump(mode = "json")
    assert response.status_code == 200
    assert response.json()['receipt_id'] == test_receipt_json['receipt_id']
    assert response.json()['title'] == test_receipt_json['title']
    assert response.json()['amount'] == test_receipt_json['amount']
    assert response.json()['items'] == test_receipt_json['items']
