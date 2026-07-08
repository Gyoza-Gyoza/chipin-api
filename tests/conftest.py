import decimal
import pytest
from datetime import datetime
from authentication.users import User
from data.items import Item
from data.receipts import Receipt, ReceiptData
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def test_receipt(test_item, created_user):
    return Receipt(owner_id = created_user['user_id'],
                   title = "Unit Testing Test Receipt",
                   date = datetime.now(),
                   items = [test_item],
                   )
@pytest.fixture
def test_receipt_data(test_item, created_user, created_receipt, test_receipt):
    total_cost = 0
    for item in created_receipt.items:
        total_cost += item.amount
    return ReceiptData(receipt_id = created_receipt['receipt_id'],
                       title = created_receipt['title'],
                       date = created_receipt['date'],
                       amount = created_receipt['amount'],
                       items = created_receipt['items'])
@pytest.fixture
def created_receipt(test_receipt):
    client = TestClient(app)
    full_receipt = test_receipt.model_dump(mode = "json")
    response = client.post(
        "/receipts",
        json = full_receipt)

    merged = response.json() | full_receipt

    yield merged

    client.delete(f"/receipts/{merged['receipt_id']}")
@pytest.fixture
def test_item():
    return Item(title = "Unit Testing Test Item",
                amount = decimal.Decimal("10.00"),
                item_count = 1)

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
    full_user = test_user.model_dump(mode = "json")
    response = client.post(
        "/users",
        json = full_user)

    merged = response.json() | full_user

    yield merged

    client.delete(f"/users/{merged['user_id']}")
