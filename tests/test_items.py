from fastapi.testclient import TestClient

from data.items import UpdateSharerRequest
from main import app

def test_get_item(created_item):
    client = TestClient(app)

    response = client.get(f"/items/{created_item.item_id}")
    returned_item = response.json()

    assert response.status_code == 200
    assert created_item.model_dump(mode = "json") == returned_item
def test_update_sharers(created_user, created_item):
    client = TestClient(app)

    response = client.put(
        f"/items/paid_by/{created_user['user_id']}",
        json = UpdateSharerRequest(item_ids = [created_item.item_id,],
                                   state = False).model_dump(mode = "json")
    )
    assert response.status_code == 200

    updated_item = client.get(f"/items/{created_item.item_id}").json()
    assert created_user['user_id'] not in updated_item['current_sharers']

    response = client.put(
        f"/items/paid_by/{created_user['user_id']}",
        json = UpdateSharerRequest(item_ids = [created_item.item_id, ],
                                 state = True).model_dump(mode = "json")
    )
    updated_item = client.get(f"/items/{created_item.item_id}").json()
    assert created_user['user_id'] in updated_item['current_sharers']
