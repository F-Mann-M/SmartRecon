from db.models import ReconciliationModel, TransactionModel, InvoiceModel
import re
from typing import List, Tuple, Optional
from datetime import timedelta
from sqlalchemy.orm import Session

LEGAL_ENTITY_TOKENS = {
    "ag",
    "gmbh",
    "mbh",
    "ug",
    "kg",
    "se",
    "ltd",
    "llc",
    "inc",
    "corp",
    "company",
    "co",
}


def _normalize_vendor_tokens(vendor_name: str) -> set[str]:
    """ Normalizes vendor names by lowercasing, removing punctuation, and filtering out common legal entity tokens. """
    cleaned = re.sub(r"[^a-z0-9\s]", " ", vendor_name.lower())
    return {
        token
        for token in cleaned.split()
        if len(token) > 1 and token not in LEGAL_ENTITY_TOKENS
    }


def get_vendor_name_similarity(invoice_vendor_name: str, transaction_vendor_name: str) -> tuple[bool, set[str]]:
    """ Compares vendor names by their normalized tokens and returns a similarity flag and common tokens. """
    invoice_tokens = _normalize_vendor_tokens(invoice_vendor_name)
    transaction_tokens = _normalize_vendor_tokens(transaction_vendor_name)
    common_tokens = invoice_tokens & transaction_tokens
    return len(common_tokens) > 0, common_tokens


def get_date_similarity(invoice_date, transaction_date) -> bool:
    """compares the transaction date with the invoice date, allowing for a window of 5 days before and 15 days after the invoice date."""
    min_date = invoice_date - timedelta(days=5)
    max_date = invoice_date + timedelta(days=15)
    return min_date <= transaction_date <= max_date


def find_best_invoice_match(db: Session, transactions: TransactionModel) -> Tuple[Optional[InvoiceModel], float, str]:
    """
    Finds the best matching invoice for a transaction using a hybrid 
    deterministic (SQL) and vector similarity approach.
    """
    try:
        transaction_matches = []
        for transaction in transactions:
            # search and compare amount between transaction and invoices
            transaction_amount = float(transaction.amount)
                        
            # search for invoices with the same total amount as the transaction
            exact_matches = db.query(InvoiceModel).filter(
                InvoiceModel.total_amount == (transaction_amount * -1)
            ).all()
            if exact_matches:
                print(f"Found {len(exact_matches)} exact matches for transaction amount {transaction_amount}.")
            
            for match in exact_matches:
                print(f"\nInvoice Vendor name: {match.vendor_name} \nTransaction Vendor name: {transaction.vendor_name}")
                # compare transaction period with invoice date (3 days before invoice date until 15 day after invoice date)
                is_with_in_windows = get_date_similarity(match.invoice_date, transaction.transaction_date)
                
                # compare vendor names between transaction and invoice
                is_vendor_name_similar, common_tokens = get_vendor_name_similarity(match.vendor_name, transaction.vendor_name)
                print(f"Vendor name similarity: {is_vendor_name_similar}, Common tokens: {common_tokens}")
                
                if is_with_in_windows and is_vendor_name_similar:
                    print(f"Exact match found: Invoice ID {match.id}, \nInvoice Vendor: {match.vendor_name}, Amount: {match.total_amount}, Date: {match.invoice_date}, \ntransaction Vendor: {transaction.vendor_name}, Amount: {transaction_amount} Transaction Date: {transaction.transaction_date}")
                    transaction_matches.append((transaction, match))
        
        print(f"Found {len(transaction_matches)} exact matches for transaction.")
        for bank_transaction, match in transaction_matches:
            print(f"\nExact match found: Invoice ID {match.id}, \nInvoice Vendor: {match.vendor_name}, Amount: {match.total_amount}, Date: {match.invoice_date}, \ntransaction Vendor: {bank_transaction.vendor_name}, Amount: {bank_transaction.amount} Transaction Date: {bank_transaction.transaction_date}")
        
            if is_match_already_reconciled(db=db, transaction_id=bank_transaction.id, invoice_id=match.id):
                print(f"Match between Transaction ID {bank_transaction.id} and Invoice ID {match.id} is already reconciled. Skipping.")
                continue
            
            # Add the match to the reconciliation table
            add_matches_to_reconciliation_table(db=db, transaction=bank_transaction, invoice=match, match_score=1.0, match_type="EXACT_MATCH")
            print(f"Added reconciliation entry for Transaction ID {bank_transaction.id} and Invoice ID {match.id}.")
            
            
            
            return
    
    except Exception as e:
        print(f"Error while finding matches between invoices and bank transactions:\n{e}")
        
    return None, 0.0, "NO_MATCH_FOUND"
    
    
def add_matches_to_reconciliation_table(db: Session, transaction: TransactionModel, invoice: InvoiceModel, match_score: float, match_type: str) -> None:
    """
    Adds a matched transaction and invoice to the reconciliation table.
    """
    try:
        reconciliation_entry = ReconciliationModel(
            transaction_id=transaction.id,
            invoice_id=invoice.id,
            confidence_score=match_score,
            match_type=match_type,
        )
        db.add(reconciliation_entry)
        db.flush()
        
        # Update the transaction status to "RECONCILED"
        transaction.status = "RECONCILED"
        db.add(transaction)
        
        db.commit()
        print(f"Added reconciliation entry for Transaction ID {transaction.id} and Invoice ID {invoice.id}.")
    except Exception as e:
        db.rollback()
        print(f"Error while adding reconciliation entry:\n{e}")


def is_match_already_reconciled(db: Session, transaction_id: str, invoice_id: str) -> bool:
    """
    Checks if a given transaction and invoice pair is already reconciled.
    """
    existing_entry = db.query(ReconciliationModel).filter_by(
        transaction_id=transaction_id,
        invoice_id=invoice_id
    ).first()
    
    return existing_entry is not None


def get_all_reconciliation_entries(db: Session) -> List[ReconciliationModel]:
    return db.query(ReconciliationModel).all()


    