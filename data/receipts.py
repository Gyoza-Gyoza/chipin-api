from fastapi import APIRouter, status
from pydantic import BaseModel, computed_field, Field
from database import get_connection
import decimal
from datetime import datetime
from psycopg import cursor
from data.items import Item

class Receipt(BaseModel):
    owner_id: int
    description: str
    date: datetime = datetime.now()
    items: list[Item]
class ReceiptUpdate(BaseModel):
    description: str
    items: list[Item]
class ReceiptIDs(BaseModel):
    receipt_id: int
    date: datetime
    item_ids: list[int]
class ReceiptData(BaseModel):
    description: str
    date: datetime
    amount: decimal.Decimal = Field(10)
    items: list[Item]
    @computed_field
    @property
    def service_tax_amount(self) -> decimal.Decimal:
        return self.amount + self.amount * current_service_tax
    @computed_field
    @property
    def gst_amount(self) -> decimal.Decimal:
        return self.amount + self.amount * current_gst
    @computed_field
    @property
    def both_amount(self) -> decimal.Decimal:
        return self.amount + self.amount * (current_service_tax + current_gst)

current_service_tax = decimal.Decimal('0.1')
current_gst = decimal.Decimal('0.09')

router = APIRouter(
    prefix="/receipts",
    tags=["Receipts"]
)

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model = Receipt
)
def create_receipt(receipt: Receipt):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        total_cost = 0
        for item in receipt.items:
            total_cost += item.amount

        cursor.execute("""
        INSERT INTO receipts (owner_id, amount, created_at, description)
        VALUES (%s, %s, %s, %s)
        RETURNING receipt_id, created_at""",
                       (receipt.owner_id, total_cost, receipt.date, receipt.description))

        row = cursor.fetchone()
        # sql query returns the ids in a row
        # cursor.fetchone gets that row from the query
        # now that row contains the columns receipt_id and date
        # store these results in the appropriate values
        receipt_id = row['receipt_id']
        date = row['date']

        item_ids = add_items(cursor, receipt_id, receipt.items)

        conn.commit()
        return ReceiptIDs(receipt_id=receipt_id,
                          date=date,
                          item_ids=item_ids)

    except Exception as e:
        conn.rollback()
        print(type(e))
        print(e)
        raise

    finally:
        cursor.close()
        conn.close()

@router.get(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model = ReceiptData
)
def get_receipt_by_user_id(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        SELECT receipt_id, description, amount, created_at FROM receipts
        WHERE owner_id = %s""",
                       (user_id,))

        return cursor.fetchall()

    except Exception as e:
        print(type(e))
        print(e)
        raise

    finally:
        cursor.close()
        conn.close()

@router.get(
    "/{receipt_id}",
    status_code=status.HTTP_200_OK,
    response_model = ReceiptData,
)
def get_receipt_by_receipt_id(receipt_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        SELECT * FROM receipts 
        LEFT JOIN items on receipts.receipt_id = items.receipt_id
        WHERE receipts.receipt_id = %s""",
                       (receipt_id,))
        row = cursor.fetchall()

        items = []
        for item in row:
            items.append(Item(payer_id = item['payer_id'],
                              amount = item['amount'],
                              description = item['description']))

        receipt_data = ReceiptData(description = row[0]['description'],
                                   amount = row[0]['amount'],
                                   date = row[0]['date'],
                                   items = items)
        return receipt_data

    except Exception as e:
        print(type(e))
        print(e)
        raise

@router.put(
    "/{receipt_id}",
    status_code=status.HTTP_200_OK
)
def update_receipt(receipt_id: int, new_receipt: ReceiptUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        UPDATE receipts SET description = %s 
        WHERE receipt_id = %s""",
                       (new_receipt.description, receipt_id))

        cursor.execute("""
        DELETE FROM items
        WHERE receipt_id = %s""",
                       (receipt_id,))

        add_items(cursor, receipt_id, new_receipt.items)

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
    "/{receipt_id}",
    status_code = status.HTTP_204_NO_CONTENT
)
def delete_receipt(receipt_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        DELETE FROM receipts 
        WHERE receipt_id = %s""",
                       (receipt_id,))
        cursor.commit()

    except Exception as e:
        conn.rollback()
        print(type(e))
        print(e)
        raise

    finally:
        cursor.close()
        conn.close()

def add_items(cursor: cursor, receipt_id: int, items: list[Item]):
    item_ids = []
    for item in items:
        cursor.execute("""
                INSERT INTO items (receipt_id, payer_id, amount, description)
                VALUES (%s, %s, %s, %s)
                RETURNING item_id""",
                       (receipt_id, item.payer_id, item.amount, item.description))
        item_ids.append(cursor.fetchone()['item_id'])

    return item_ids