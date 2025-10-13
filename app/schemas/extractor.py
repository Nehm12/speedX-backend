from typing import List, Optional
from pydantic import BaseModel


class Transaction(BaseModel):
    date: Optional[str]
    document_number: Optional[str]
    bank_code: Optional[str]
    account_number: Optional[str]
    description: str
    debit: float
    credit: float

class BankStatementResponse(BaseModel):
    bank_name: str
    account_number: Optional[str]
    account_holder: Optional[str]
    transactions: List[Transaction]
    starting_date: Optional[str]
    closing_date: Optional[str]
    starting_balance: Optional[float]
    closing_balance: Optional[float]
    currency: Optional[str]

