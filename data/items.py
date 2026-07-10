from fastapi import APIRouter, status, HTTPException
from data.database import get_connection
from pydantic import BaseModel, Field
import decimal
from psycopg import cursor

class Item(BaseModel):
    title: str
    amount: decimal.Decimal = Field(10)
    item_count: int = Field(1)
class ItemData(BaseModel):
    item_id: int
    title: str
    amount: decimal.Decimal = Field(10)
    item_count: int = Field(1)
    current_sharers: list[int] = []
class UpdateSharerRequest(BaseModel):
    item_ids: list[int]
    state: bool

router = APIRouter(
    prefix = "/items",
    tags = ["Items"]
)

@router.get(
    "/{item_id}",
    status_code = status.HTTP_200_OK,
    response_model = ItemData
)
def get_item_data(item_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        SELECT title, amount, item_count, array_agg(item_payers.user_id) AS current_sharers
        FROM items LEFT JOIN item_payers
        ON items.item_id = item_payers.item_id
        WHERE items.item_id = %s
        GROUP BY title, amount, item_count""",
                       (item_id,))

        item_data = cursor.fetchone()
        current_sharers =[]
        for user_id in item_data['current_sharers']:
            if user_id is not None:
                print(user_id)
                current_sharers.append(int(user_id))

        print(item_data)
        return ItemData(item_id = item_id,
                        title = item_data['title'],
                        amount = item_data['amount'],
                        item_count = item_data['item_count'],
                        current_sharers = current_sharers)

    except Exception as e:
        print(type(e))
        print(e)
        raise

    finally:
        cursor.close()
        conn.close()
@router.put(
    "/paid_by/{user_id}",
    status_code = status.HTTP_200_OK
)
def update_sharers(user_id: int, update_sharers_request: UpdateSharerRequest):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        for item_id in update_sharers_request.item_ids:
            cursor.execute("""
                           DELETE FROM item_payers
                           WHERE item_id = %s AND user_id = %s""",
                           (item_id, user_id))

            if update_sharers_request.state:
                cursor.execute("""
                INSERT INTO item_payers (item_id, user_id) 
                VALUES (%s, %s)""",
                               (item_id, user_id))

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(type(e))
        print(e)
        raise

    finally:
        cursor.close()
        conn.close()

    if update_sharers_request.state:
        return {"message": "Sharer added"}
    else:
        return {"message": "Sharer removed"}

# @router.put(
#     "/{item_id}",
#     status_code = status.HTTP_200_OK
# )
# def set_item_state(state: bool, item_id: int):
#     conn = get_connection()
#     cursor = conn.cursor()
#
#     try:
#         cursor.execute("""
#         UPDATE items SET paid = %s
#         WHERE item_id = %s""",
#                        (state, item_id))
#         conn.commit()
#
#     except Exception as e:
#         conn.rollback()
#         print(type(e))
#         print(e)
#         raise
#
#     finally:
#         cursor.close()
#         conn.close()

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
                INSERT INTO items (receipt_id, amount, title, item_count)
                VALUES (%s, %s, %s, %s)
                RETURNING item_id""",
                       (receipt_id, item.amount, item.title, item.item_count))
        item_ids.append(cursor.fetchone()['item_id'])

    return item_ids
