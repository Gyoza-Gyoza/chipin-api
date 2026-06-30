import datetime
from fastapi import APIRouter, HTTPException, status
from psycopg import cursor
from pydantic import BaseModel
from data.database import get_connection

class Expense(BaseModel):
    payer_id: int
    amount: int
    description: str

class Expenses(BaseModel):
    expenses: list[Expense]

class ExpenseData(BaseModel):
    expense_id: int
    receipt_id: int
    owner_id: int
    amount: int
    payer_id: int
    description: str
    created_at: datetime.datetime

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"],
)

@router.post(
    "/",
    status_code = status.HTTP_201_CREATED
)
def create_expense(expense: Expense):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        expense_id = insert_expense(cursor, expense)
        print(expense_id)

        conn.commit()
        conn.close()

        return {'expense_id' : expense_id['expense_id']}

    except Exception as e:
        print(type(e))
        print(e)

@router.post(
    "/multi",
    status_code = status.HTTP_201_CREATED
)
def create_expenses(expenses: Expenses):
    try:
        for expense in expenses.expenses:
            create_expense(expense)

    except Exception as e:
        print(type(e))
        print(e)


def insert_expense(cursor: cursor, expense : Expense):
    cursor.execute("""
                            INSERT INTO expenses (user_id, amount, borrower_id, description) 
                            VALUES (%s, %s, %s, %s)
                            RETURNING expense_id""",
                   (expense.user_id, expense.amount, expense.borrower_id, expense.description))
    return cursor.fetchone()['expense_id']

@router.get(
    "/",
    status_code = status.HTTP_200_OK
)
def get_expenses(user_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM expenses WHERE user_id=%s", (user_id,))

        expense = cursor.fetchall()

        if expense is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                          detail="User not found")

        return expense

    except Exception as e:
        print(type(e))
        print(e)