from fastapi.testclient import TestClient
from main import app

def test_get_item(created_item):
    client = TestClient(app)

    response = client.get(f"/items/{created_item.item_id}")
    returned_item = response.json()

    assert response.status_code == 200
    assert created_item.model_dump(mode = "json") == returned_item
#
# def test_update_sharers(created_user, created_receipt, created_item):
#     client = TestClient(app)
#
#     item_to_test = created_receipt.items[0]
#     initial_sharers = client.get(f"/items/{item_to_test}")
#     initial_receipt = client.get(f"/receipts/{created_receipt['receipt_id']}").json()
#
#     response = client.put(
#         f"/paid_by/{created_user['user_id']}",
#         json = created_receipt['item_ids'].model_dump(mode = "json")
#     )