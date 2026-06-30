from fastapi import APIRouter, status, HTTPException
from data.database import get_connection
from pydantic import BaseModel, Field
import decimal

class Item(BaseModel):
    payer_id: list[int]
    amount: decimal.Decimal = Field(10)
    description: str

router = APIRouter(
    prefix = "/items",
    tags = ["Items"]
)

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
