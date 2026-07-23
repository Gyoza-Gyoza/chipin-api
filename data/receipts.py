from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, computed_field, Field
from data.database import get_connection
import decimal
from datetime import datetime
from data.items import Item, initialize_items

class Receipt(BaseModel):
    owner_id: int
    sharer_ids: list[int]
    title: str
    date: datetime = datetime.now()
    items: list[Item]
class ReceiptUpdate(BaseModel):
    title: str
    sharer_ids: list[int]
    items: list[Item]
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
    prefix = "/receipts",
    tags = ["Receipts"]
)

@router.post(
    "/",
    status_code = status.HTTP_201_CREATED,
    response_model = ReceiptIDs
)
def create_receipt(receipt: Receipt):
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
    "/users/{user_id}",
    status_code = status.HTTP_200_OK,
    response_model = list[ReceiptData]
)
def get_receipt_by_user_id(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        SELECT receipts.receipt_id, owner_id, title, amount, date, array_agg(receipt_sharers.sharer_id) AS sharer_ids FROM receipts
        LEFT JOIN receipt_sharers
        ON receipts.receipt_id = receipt_sharers.receipt_id
        WHERE owner_id = %s
        GROUP BY receipts.receipt_id""",
                       (user_id,))

        receipts = cursor.fetchall()

        result = []
        for receipt in receipts:
            cursor.execute("""
            SELECT * FROM items 
            WHERE receipt_id = %s""",
                           (receipt['receipt_id'],))
            itemList = cursor.fetchall()
            items = []
            for item in itemList:
                items.append(Item(amount = item['amount'],
                                  title = item['title'],
                                  item_count = item['item_count']))

            sharer_ids = []
            sharer_ids.append(user_id)
            for sharer in receipt['sharer_ids']:
                if sharer:
                    sharer_ids.append(sharer)

            result.append(ReceiptData(receipt_id = receipt['receipt_id'],
                                      owner_id = receipt['owner_id'],
                                      title = receipt['title'],
                                      amount = receipt['amount'],
                                      date = receipt['date'],
                                      items = items,
                                      sharer_ids = sharer_ids))

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
        SELECT receipts.receipt_id, owner_id, title, amount, date, array_agg(receipt_sharers.sharer_id) AS sharer_ids FROM receipts
        LEFT JOIN receipt_sharers
        ON receipts.receipt_id = receipt_sharers.receipt_id
        WHERE receipt_sharers.sharer_id = %s
        GROUP BY receipts.receipt_id""",
                       (sharer_id,))

        receipts = cursor.fetchall()

        result = []
        for receipt in receipts:
            cursor.execute("""
            SELECT * FROM items 
            WHERE receipt_id = %s""",
                           (receipt['receipt_id'],))
            itemList = cursor.fetchall()
            items = []
            for item in itemList:
                items.append(Item(amount = item['amount'],
                                  title = item['title'],
                                  item_count = item['item_count']))

            sharer_ids = []
            for sharer in receipt['sharer_ids']:
                if sharer:
                    sharer_ids.append(sharer)

            result.append(ReceiptData(receipt_id = receipt['receipt_id'],
                                      owner_id = receipt['owner_id'],
                                      title = receipt['title'],
                                      amount = receipt['amount'],
                                      date = receipt['date'],
                                      items = items,
                                      sharer_ids = sharer_ids))

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
        cursor.execute("""
        SELECT * FROM receipts 
        LEFT JOIN items on receipts.receipt_id = items.receipt_id
        WHERE receipts.receipt_id = %s""",
                       (receipt_id,))
        row = cursor.fetchall()

        if not row:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                                detail = "No items found")
        items = []
        for item in row:
            items.append(Item(amount = item['amount'],
                              title = item['title'],
                              item_count= item['item_count']))

        cursor.execute("""
        SELECT receipts.receipt_id, owner_id, title, amount, date, array_agg(receipt_sharers.sharer_id) AS sharer_ids FROM receipts
        LEFT JOIN receipt_sharers
        ON receipts.receipt_id = receipt_sharers.receipt_id
        WHERE receipts.receipt_id = %s
        GROUP BY receipts.receipt_id""",
                       (receipt_id,))
        receipt = cursor.fetchone()

        sharer_ids = []
        sharer_ids.append(receipt['owner_id'])
        for sharer in receipt['sharer_ids']:
            if sharer:
                sharer_ids.append(sharer)

        if not receipt:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                                detail = "No receipts found")

        else:
            receipt_data = ReceiptData(receipt_id = receipt_id,
                                       owner_id = receipt['owner_id'],
                                       title = receipt['title'],
                                       amount = receipt['amount'],
                                       date = receipt['date'],
                                       items = items,
                                       sharer_ids = sharer_ids)
            return receipt_data
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
        UPDATE receipts SET title = %s
        WHERE receipt_id = %s""",
                       (new_receipt.title, receipt_id))

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