from decimal import Decimal
import pytest
from datetime import datetime
from authentication.users import User
from data.items import Item, ItemData, UpdateSharerRequest
from data.receipts import Receipt, ReceiptUpdate
from fastapi.testclient import TestClient
from main import app
from data.database import get_connection
from psycopg import cursor

@pytest.fixture
def test_receipt(test_item, created_user):
    return Receipt(owner_id = created_user['user_id'],
                   title = "Unit Testing Test Receipt",
                   date = datetime.now(),
                   items = [test_item, test_item],
                   sharer_ids = [created_user['user_id'],])
@pytest.fixture
def test_receipt_update(test_item_update, created_user):
    return ReceiptUpdate(title = "Alternate Test Receipt",
                         items = [test_item_update],
                         sharer_ids = [created_user['user_id'],])
@pytest.fixture
def created_receipt(test_receipt):
    client = TestClient(app)
    receipt = test_receipt.model_dump(mode = "json")
    response = client.post(
        "/receipts",
        json = receipt)

    full_receipt = response.json() | receipt

    yield full_receipt

    client.delete(f"/receipts/{full_receipt['receipt_id']}")
@pytest.fixture
def test_item():
    return Item(title = "Unit Testing Test Item",
                amount = Decimal("10.00"),
                item_count = 1)
@pytest.fixture
def created_item(test_item, created_receipt):
    conn = get_connection()
    cursor = conn.cursor()
    client = TestClient(app)

    try:
        cursor.execute("""
        INSERT INTO items (receipt_id, title, amount, item_count)
        VALUES (%s, %s, %s, %s)
        RETURNING item_id""",
                       (created_receipt['receipt_id'],
                        test_item.title,
                        test_item.amount,
                        test_item.item_count))
        item_id = cursor.fetchone()['item_id']
        conn.commit()

        response = client.put(
            f"/items/paid_by/{created_receipt['owner_id']}",
            json = UpdateSharerRequest(item_ids = [item_id,],
                                       state = True).model_dump(mode = "json")
        )
        assert response.status_code == 200

        cursor.execute("""
        SELECT user_id FROM item_payers
        WHERE item_id = %s""", (item_id, ))
        rows = cursor.fetchall()
        user_ids = []
        for row in rows:
            user_ids.append(int(row['user_id']))

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(type(e))
        print(e)
        raise

    finally:
        cursor.close()
        conn.close()

    return ItemData(item_id = item_id,
                    title = test_item.title,
                    amount = test_item.amount,
                    item_count = test_item.item_count,
                    current_sharers = user_ids)
@pytest.fixture
def test_item_update():
    return Item(title = "Alternate Test Item",
                amount = Decimal("5.00"),
                item_count = 2)
@pytest.fixture
def test_update_sharer_request_true(created_item):
    return UpdateSharerRequest(item_ids = [created_item.item_id,],
                               state = True)
@pytest.fixture
def test_update_sharer_request_false(created_item):
    return UpdateSharerRequest(item_ids = [created_item.item_id,],
                               state = False)

@pytest.fixture
def test_user():
    return User(username = "Unit Testing Test User",
                password = "Unittestpassword",
                email = "unittesting@email.com",
                first_name = "unittesting",
                last_name = "unittesting",
                phone_number = "91234567"
                )
@pytest.fixture
def created_user(test_user):
    client = TestClient(app)
    user = test_user.model_dump(mode = "json")
    response = client.post(
        "/users",
        json = user)

    full_user = response.json() | user

    yield full_user

    client.delete(f"/users/{full_user['user_id']}")
