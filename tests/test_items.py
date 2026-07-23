from fastapi.testclient import TestClient

from data.items import UpdateSharerRequest
from main import app

# def test_get_item(created_item):
#     client = TestClient(app)
#
#     response = client.get(f"/items/{created_item.item_id}")
#     returned_item = response.json()
#
#     assert response.status_code == 200
#     assert created_item.model_dump(mode = "json") == returned_item
def test_update_sharers(created_user, created_receipt):
    client = TestClient(app)

    item_ids = []
    for item in created_receipt['items']:
        item_ids.append(item['item_id'])

    response = client.put(
        f"/items/paid_by/{created_user['user_id']}",
        json = UpdateSharerRequest(item_ids = item_ids,
                                   state = False).model_dump(mode = "json")
    )
    assert response.status_code == 200

    receipt = client.get(f"/receipts/{created_receipt['receipt_id']}").json()
    updated_item = receipt['items'][0]
    print(updated_item)
    assert updated_item['current_sharers'].count(created_user['user_id']) == 0

    response = client.put(
        f"/items/paid_by/{created_user['user_id']}",
        json = UpdateSharerRequest(item_ids = item_ids,
                                 state = True).model_dump(mode = "json")
    )
    assert response.status_code == 200

    receipt = client.get(f"/receipts/{created_receipt['receipt_id']}").json()
    updated_item = receipt['items'][0]
    assert updated_item['current_sharers'].count(created_user['user_id']) == 1
