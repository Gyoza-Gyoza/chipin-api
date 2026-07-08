from decimal import Decimal
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
                   items = [test_item, test_item],
                   )
@pytest.fixture
def test_receipt_data(test_item, created_user, created_receipt, test_receipt):
    total_cost = Decimal(0.0)
    for item in created_receipt['items']:
        total_cost += Decimal(item['amount'])
    return ReceiptData(receipt_id = created_receipt['receipt_id'],
                       title = created_receipt['title'],
                       date = created_receipt['date'],
                       amount = total_cost,
                       items = created_receipt['items'])
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
