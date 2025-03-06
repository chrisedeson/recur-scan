from datetime import datetime
from statistics import stdev

from recur_scan.transactions import Transaction


def parse_date(date_str: str) -> datetime:
    """Convert a date string to a datetime object."""
    return datetime.strptime(date_str, "%Y-%m-%d")  # Adjust format if needed


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    return len([t for t in all_transactions if t.amount == transaction.amount])


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    if not all_transactions:
        return 0.0
    return get_n_transactions_same_amount(transaction, all_transactions) / len(all_transactions)


def get_n_transactions_same_name(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    return len([t for t in all_transactions if t.name == transaction.name])


def get_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    _ = transaction  # Prevents linter warning
    """Calculate the average number of days between transactions of the same name."""
    dates = [parse_date(t.date) for t in all_transactions]  # Ensure dates are datetime objects
    if len(dates) < 2:
        return 0.0
    sorted_dates = sorted(dates)
    gaps = [(sorted_dates[i] - sorted_dates[i - 1]).days for i in range(1, len(sorted_dates))]
    return sum(gaps) / len(gaps)


def get_transaction_std_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    _ = transaction  # Prevents linter warning
    """Compute the standard deviation of transaction amounts for the same name."""
    amounts = [t.amount for t in all_transactions]
    return stdev(amounts) if len(amounts) > 1 else 0.0


def follows_regular_interval(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if transactions follow a regular pattern (~30 days apart)."""
    freq = get_transaction_frequency(transaction, all_transactions)
    return 27 <= freq <= 33 if freq > 0 else False


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int | bool]:
    return {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        "n_transactions_same_name": get_n_transactions_same_name(transaction, all_transactions),
        "transaction_frequency": get_transaction_frequency(transaction, all_transactions),
        "transaction_std_amount": get_transaction_std_amount(transaction, all_transactions),
        "follows_regular_interval": follows_regular_interval(transaction, all_transactions),
    }
