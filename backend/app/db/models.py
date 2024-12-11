from uuid import uuid4, UUID
from datetime import date, datetime
from pydantic import EmailStr, UUID4
from sqlmodel import Field, SQLModel, Relationship


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True)
    username: str = Field(unique=True)
    first_name: str
    last_name: str
    age: int
    password: str
    categories: list["Categories"] = Relationship(back_populates="user")
    budgets: list["Budget"] = Relationship(back_populates="user")
    transactions: list["Transactions"] = Relationship(back_populates="user")
    saving_pots: list["SavingPots"] = Relationship(back_populates="user")
    recurring_bills: list["RecurringBills"] = Relationship(
        back_populates="user")


class Categories(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: UUID4 = Field(foreign_key="user.id", ondelete="CASCADE")
    name: str
    description: str | None = None
    user: User = Relationship(back_populates="categories")


class Budget(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: UUID4 = Field(foreign_key="user.id",
                           ondelete="CASCADE", default=None)
    category_id: int = Field(foreign_key="categories.id", ondelete="CASCADE")
    amount: float = Field()
    start_date: date = Field()
    end_date: date = Field()
    user: User = Relationship(back_populates="budgets")


class Transactions(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: UUID4 = Field(foreign_key="user.id", ondelete="CASCADE")
    category_id: int = Field(foreign_key="categories.id", ondelete="CASCADE")
    budget_id: int = Field(foreign_key="budget.id",
                           nullable=True, ondelete="CASCADE")
    amount: float = Field()
    description: str | None = Field(default=None)
    trasaction_date: datetime = Field()
    user: User = Relationship(back_populates="transactions")


class SavingPots(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: UUID4 = Field(foreign_key="user.id", ondelete="CASCADE")
    name: str = Field()
    target_amount: float = Field()
    current_amount: float = Field(default=0.0)
    start_date: date = Field()
    user: User = Relationship(back_populates="saving_pots")


class RecurringBills(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: UUID4 = Field(foreign_key="user.id", ondelete="CASCADE")
    name: str = Field()
    amount: float = Field()
    due_date: str = Field()
    is_paid: bool = Field(default=False)
    user: User = Relationship(back_populates="recurring_bills")
