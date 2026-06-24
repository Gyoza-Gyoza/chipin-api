from fastapi import APIRouter, status, HTTPException
from database import get_connection
from pydantic import BaseModel, Field
import decimal
from psycopg import cursor
class Item(BaseModel):
    amount: decimal.Decimal = Field(10)
    title: str

router = APIRouter(
    prefix = "/items",
    tags = ["Items"]
)
# Maybe do this for multiple? Like add all items that the user wants to pay for and then
# post them all in one function and return the calculation
@router.post(
    "/paid_by/{user_id}",
    status_code = status.HTTP_201_CREATED
)
def add_sharers(item_id: int, user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO item_payers (item_id, user_id) 
        VALUES (%s, %s)""",
                       item_id, user_id)
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(type(e))
        print(e)
        raise

    finally:
        cursor.close()
        conn.close()

    return {"message": "Sharer added"}

@router.get(
    "/",
    status_code = status.HTTP_200_OK,
    response_model = list[Item]
)
def get_item():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM items""")

    items = cursor.fetchall()

    cursor.close()
    conn.close()

    return items

# Change to adding sharers instead of items
@router.get(
    "/{item_id}",
    status_code = status.HTTP_200_OK,
    response_model = Item
)
def get_item(item_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        SELECT * FROM items 
        WHERE item_id = %s""",
                       (item_id,))

        item = cursor.fetchone()

        if item is None:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                                detail = "Item not found")
    except Exception as e:
        conn.rollback()
        print(type(e))
        print(e)
        raise

    finally:
        cursor.close()
        conn.close()

    return item

# Add function for editing sharers and one for editing items
@router.put(
    "/{item_id}",
    status_code = status.HTTP_200_OK
)
def set_item_state(state: bool, item_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        UPDATE items SET paid = %s
        WHERE item_id = %s""",
                       (state, item_id))
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(type(e))
        print(e)
        raise

    finally:
        cursor.close()
        conn.close()

@router.delete(
    "/{item_id}",
    status_code = status.HTTP_200_OK
)
def delete_item(item_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        DELETE FROM items
        WHERE item_id = %s""",
                       (item_id,))
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(type(e))
        print(e)
        raise

    finally:
        cursor.close()
        conn.close()

def initialize_items(cursor: cursor, receipt_id: int, items: list[Item]):
    item_ids = []
    for item in items:
        cursor.execute("""
                INSERT INTO items (receipt_id, amount, title)
                VALUES (%s, %s, %s)
                RETURNING item_id""",
                       (receipt_id, item.amount, item.title))
        item_ids.append(cursor.fetchone()['item_id'])

    return item_ids
