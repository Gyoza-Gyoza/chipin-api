from fastapi import APIRouter, status
from pydantic import BaseModel
from database import get_connection
import datetime
class Receipt(BaseModel):
    owner_id: int
    description: str
    items: list[Item]
class Item(BaseModel):
    payer_id: int
    amount: int
    description: str
class ReceiptData(BaseModel):
    receipt_id: int
    created_at: datetime.datetime
    item_ids: list[int]

router = APIRouter(
    prefix="/receipts",
    tags=["Receipts"]
)

@router.post(
    "/",
status_code=status.HTTP_201_CREATED
)
def create_receipt(receipt: Receipt):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        total_cost = 0
        for item in receipt.items:
            total_cost += item.amount

        cursor.execute("""
        INSERT INTO receipts (owner_id, amount, description)
        VALUES (%s, %s, %s)
        RETURNING receipt_id, created_at""",
                     (receipt.owner_id, total_cost, receipt.description))

        row = cursor.fetchone()
        receipt_id = row['receipt_id']
        created_at = row['created_at']

        item_ids = []
        for item in receipt.items:
            cursor.execute("""
            INSERT INTO items (receipt_id, payer_id, amount, description)
            VALUES (%s, %s, %s, %s)
            RETURNING item_id""",
                         (receipt_id, item.payer_id, item.amount, item.description))
            item_ids.append(cursor.fetchone()['item_id'])

        conn.commit()
        return ReceiptData(receipt_id=receipt_id, created_at=created_at, item_ids=item_ids)

    except Exception as e:
        conn.rollback()
        print(type(e))
        print(e)
        raise

    finally:
        cursor.close()
        conn.close()