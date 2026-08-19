from db.models import TransactionModel, InvoiceModel
from typing import Tuple
from datetime import timedelta

def find_best_invoice_match(db: Session, transactions: TransactionModel)-> Tuple[Optional[InvoiceModel, float, str]]:
    """
    Finds the best matching invoice for a transaction using a hybrid 
    deterministic and vector similarity approach.
    """

    # search and compare amount between transaction and invoices
    transaction_amount = abs(float(transactions.amount))

    exact_matches = db.query(InvoiceModel).filter(
        InvoiceModel.total_amount == transaction_amount
    ).all()

    # compare transaction period with invoice date (3 days before invoice date until 15 day after invoice date)
    transaction_date = transactions.transaction_date
    min_date = exact_matches.invoice_date - timedelta(days=3)
    max_date = exact_matches.invoice_date + timedelta(days=15)

    is_with_in_windows = min_date <= transaction_date <= max_date

    for match in exact_matches:
        if match.vendor_name.lower() in transactions.vendor_name.lower():
            return match, 1.0, "EXACT_AMOUNT_AND_VENDOR"
    
    # currency
    pass