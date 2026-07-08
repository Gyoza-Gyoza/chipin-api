import decimal
import pytest
from datetime import datetime
from authentication.users import User
from data.items import Item
from data.receipts import Receipt
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def created_user(test_user):
    client = TestClient(app)
    response = client.post(
        "/users",
        json = test_user.model_dump(mode = "json"))

    yield response.json()

    client.delete(f"/users/{response.json()['user_id']}")

@pytest.fixture
def test_receipt(test_item, created_user):
    return Receipt(owner_id = created_user['user_id'],
                   title = "Unit Testing Test Receipt",
                   date = datetime.now(),
                   items = [test_item],
                   )
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