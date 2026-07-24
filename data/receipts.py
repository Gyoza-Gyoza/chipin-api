from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, computed_field, Field
from data.database import get_connection
import decimal
from datetime import datetime
from data.items import Item, ItemData, get_items_of_receipt, initialize_items
from psycopg import cursor

class Receipt(BaseModel):
    owner_id: int
    sharer_ids: list[int]
    title: str
    date: datetime = datetime.now()
    items: list[ItemData] | None

class ReceiptCreate(BaseModel):
    owner_id: int
    sharer_ids: list[int]
    title: str
    date: datetime = datetime.now()
    items: list[Item] | None
class ReceiptUpdate(BaseModel):
    title: str
    sharer_ids: list[int]
    items: list[Item]
    qr_ready: bool
class ReceiptIDs(BaseModel):
    receipt_id: int
    date: datetime
    item_ids: list[int]
class ReceiptData(BaseModel):
    receipt_id: int
    owner_id: int
    sharer_ids: list[int]
    title: str
    date: datetime
    items: list[ItemData] | None
    qr_ready: bool
    @computed_field
    @property
    def amount(self) -> decimal.Decimal:
        result = decimal.Decimal(0)
        for item in self.items:
            result += item.amount
        return result
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
    prefix = "/receipts",
    tags = ["Receipts"]
)

@router.post(
    "/",
    status_code = status.HTTP_201_CREATED,
    response_model = ReceiptIDs
)
def create_receipt(receipt: ReceiptCreate):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        total_cost = 0
        for item in receipt.items:
            total_cost += item.amount

        cursor.execute("""
        INSERT INTO receipts (owner_id, amount, date, title)
        VALUES (%s, %s, %s, %s)
        RETURNING receipt_id, date""",
                       (receipt.owner_id, total_cost, receipt.date, receipt.title))

        row = cursor.fetchone()
        # sql query returns the ids in a row
        # cursor.fetchone gets that row from the query
        # now that row contains the columns receipt_id and date
        # store these results in the appropriate values
        receipt_id = row['receipt_id']
        date = row['date']

        item_ids = initialize_items(cursor, receipt_id, receipt.items)

        for sharer in receipt.sharer_ids:
            cursor.execute("""
            INSERT INTO receipt_sharers (receipt_id, sharer_id)
            VALUES (%s, %s)""",
                           (receipt_id, sharer))
        conn.commit()
        return ReceiptIDs(receipt_id = receipt_id,
                          date = date,
                          item_ids = item_ids)

    except Exception as e:
        conn.rollback()
        print(type(e))
        print(e)
        raise

    finally:
        cursor.close()
        conn.close()

@router.get(
    "/users/{user_id}/get-all",
    response_model = list[ReceiptData]
)
def get_all_receipts_by_id(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        SELECT DISTINCT(receipts.receipt_id) FROM receipts LEFT JOIN receipt_sharers
        ON receipts.receipt_id = receipt_sharers.receipt_id
        WHERE owner_id = %s OR sharer_id = %s""",
                       (user_id, user_id))
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append(get_receipt_by_id(cursor, row['receipt_id']))

        return result

    except Exception as e:
        print(type(e))
        print(e)
        raise

    finally:
        cursor.close()
        conn.close()


@router.get(
    "/users/{user_id}",
    status_code = status.HTTP_200_OK,
    response_model = list[ReceiptData]
)
def get_receipt_by_user_id(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        SELECT receipts.receipt_id, owner_id, title, amount, date, qr_ready, array_agg(receipt_sharers.sharer_id) AS sharer_ids FROM receipts
        LEFT JOIN receipt_sharers
        ON receipts.receipt_id = receipt_sharers.receipt_id
        WHERE owner_id = %s
        GROUP BY receipts.receipt_id""",
                       (user_id,))

        receipts = cursor.fetchall()

        result = []
        for receipt in receipts:
            sharer_ids = []
            sharer_ids.append(user_id)
            for sharer in receipt['sharer_ids']:
                if sharer:
                    sharer_ids.append(sharer)

            result.append(ReceiptData(receipt_id = receipt['receipt_id'],
                                      owner_id = receipt['owner_id'],
                                      title = receipt['title'],
                                      date = receipt['date'],
                                      items = get_items_of_receipt(cursor, receipt['receipt_id']),
                                      sharer_ids = sharer_ids,
                                      qr_ready = receipt['qr_ready']))

        return result

    except Exception as e:
        print(type(e))
        print(e)
        raise

    finally:
        cursor.close()
        conn.close()

@router.get(
    "/users/sharers/{sharer_id}",
    status_code = status.HTTP_200_OK,
    response_model = list[ReceiptData]
)
def get_receipt_by_sharer_id(sharer_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        SELECT receipts.receipt_id, owner_id, title, amount, date, qr_ready, array_agg(receipt_sharers.sharer_id) AS sharer_ids FROM receipts
        LEFT JOIN receipt_sharers
        ON receipts.receipt_id = receipt_sharers.receipt_id
        WHERE receipt_sharers.sharer_id = %s
        GROUP BY receipts.receipt_id""",
                       (sharer_id,))

        receipts = cursor.fetchall()

        result = []
        for receipt in receipts:
            sharer_ids = []
            sharer_ids.append(receipt['owner_id'])
            for sharer in receipt['sharer_ids']:
                if sharer:
                    sharer_ids.append(sharer)

            result.append(ReceiptData(receipt_id = receipt['receipt_id'],
                                      owner_id = receipt['owner_id'],
                                      title = receipt['title'],
                                      date = receipt['date'],
                                      items = get_items_of_receipt(cursor, receipt['receipt_id']),
                                      sharer_ids = sharer_ids,
                                      qr_ready = receipt['qr_ready']))

        return result

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
        return get_receipt_by_id(cursor, receipt_id)
    except Exception as e:
        print(type(e))
        print(e)
        raise
    finally:
        cursor.close()
        conn.close()

@router.put(
    "/{receipt_id}",
    status_code = status.HTTP_200_OK
)
def update_receipt(receipt_id: int, new_receipt: ReceiptUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        UPDATE receipts SET title = %s, qr_ready = %s
        WHERE receipt_id = %s""",
                       (new_receipt.title, new_receipt.qr_ready, receipt_id))

        cursor.execute("""
        DELETE FROM receipt_sharers 
        WHERE receipt_id = %s""", (receipt_id,))

        for sharers in new_receipt.sharer_ids:
            cursor.execute("""
            INSERT INTO receipt_sharers
            (receipt_id, sharer_id)
            VALUES (%s, %s)""", (receipt_id, sharers))

        cursor.execute("""
        DELETE FROM items
        WHERE receipt_id = %s""",
                       (receipt_id,))

        initialize_items(cursor, receipt_id, new_receipt.items)

        conn.commit()
        return {"message": "Receipt updated successfully"}

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
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(type(e))
        print(e)
        raise

    finally:
        cursor.close()
        conn.close()

def get_receipt_by_id(cursor: cursor, receipt_id: int):
    cursor.execute("""
           SELECT receipts.receipt_id, owner_id, title, amount, date, qr_ready, array_agg(receipt_sharers.sharer_id) AS sharer_ids FROM receipts
           LEFT JOIN receipt_sharers
           ON receipts.receipt_id = receipt_sharers.receipt_id
           WHERE receipts.receipt_id = %s
           GROUP BY receipts.receipt_id""",
                   (receipt_id,))
    receipt = cursor.fetchone()

    sharer_ids = []
    if receipt:
        sharer_ids.append(receipt['owner_id'])
        for sharer in receipt['sharer_ids']:
            if sharer:
                if sharer not in sharer_ids:
                    sharer_ids.append(sharer)

    if not receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No receipts found")

    else:
        receipt_data = ReceiptData(receipt_id=receipt_id,
                                   owner_id=receipt['owner_id'],
                                   title=receipt['title'],
                                   date=receipt['date'],
                                   items=get_items_of_receipt(cursor, receipt['receipt_id']),
                                   sharer_ids=sharer_ids,
                                   qr_ready=receipt['qr_ready'])
    return receipt_data