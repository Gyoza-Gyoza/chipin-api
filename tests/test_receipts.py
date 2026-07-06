from fastapi.testclient import TestClient
from main import app

def test_create_receipt(test_receipt):
    client = TestClient(app)
    response = client.post(
        "/receipts",
        json = test_receipt.model_dump(mode = "json"))
    assert response.status_code == 201

# def test_get_receipt():
#     client = TestClient(app)
#     response = client.get("/receipts/")
#
#     assert response.status_code == 200