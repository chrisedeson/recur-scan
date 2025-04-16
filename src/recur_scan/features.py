from datetime import datetime
from statistics import StatisticsError, median, stdev

from recur_scan.transactions import Transaction


def parse_date(date_str: str) -> datetime:
    """Convert a date string to a datetime object."""
    return datetime.strptime(date_str, "%Y-%m-%d")


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """
    Count transactions with amounts that match within a 1% tolerance.
    This tolerance helps capture minor variations due to rounding.
    """
    tol = 0.01 * transaction.amount if transaction.amount != 0 else 0.01
    return sum(1 for t in all_transactions if abs(t.amount - transaction.amount) <= tol)


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the percentage of transactions with nearly the same amount."""
    count = get_n_transactions_same_amount(transaction, all_transactions)
    return count / len(all_transactions) if all_transactions else 0.0


def get_n_transactions_same_name(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Count transactions with the same merchant name."""
    return sum(1 for t in all_transactions if t.name == transaction.name)


def get_transaction_gaps(all_transactions: list[Transaction]) -> list[int]:
    """Get the number of days between consecutive transactions."""
    try:
        dates = sorted(parse_date(t.date) for t in all_transactions)
    except Exception:
        return []
    return [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))] if len(dates) > 1 else []


def get_transaction_frequency(all_transactions: list[Transaction]) -> float:
    """Calculate the average number of days between transactions."""
    gaps = get_transaction_gaps(all_transactions)
    return sum(gaps) / len(gaps) if gaps else 0.0


def get_transaction_std_amount(all_transactions: list[Transaction]) -> float:
    """Compute the standard deviation of transaction amounts."""
    amounts = [t.amount for t in all_transactions]
    try:
        return stdev(amounts) if len(amounts) > 1 else 0.0
    except StatisticsError:
        return 0.0


def std_amount_all(all_transactions: list[Transaction]) -> float:
    """
    Compute the standard deviation of transaction amounts for a list of transactions.
    """
    amounts = [t.amount for t in all_transactions]
    try:
        return stdev(amounts) if len(amounts) > 1 else 0.0
    except StatisticsError:
        return 0.0


def get_coefficient_of_variation(all_transactions: list[Transaction]) -> float:
    """
    Compute the coefficient of variation (std/mean) for transaction amounts.
    """
    amounts = [t.amount for t in all_transactions]
    if not amounts:
        return 0.0
    avg = sum(amounts) / len(amounts)
    if avg == 0:
        return 0.0
    return std_amount_all(all_transactions) / avg


def follows_regular_interval(all_transactions: list[Transaction]) -> bool:
    """
    Check if transactions follow a regular pattern (~monthly).
    """
    gaps = get_transaction_gaps(all_transactions)
    if not gaps:
        return False
    avg_gap = sum(gaps) / len(gaps)
    try:
        gap_std = stdev(gaps) if len(gaps) > 1 else 0.0
    except StatisticsError:
        gap_std = 0.0
    return (27 <= avg_gap <= 33) and (gap_std < 3)


def detect_skipped_months(all_transactions: list[Transaction]) -> int:
    """Count how many months were skipped in a recurring pattern."""
    try:
        dates = sorted(parse_date(t.date) for t in all_transactions)
    except Exception:
        return 0
    if not dates:
        return 0
    months = {d.year * 12 + d.month for d in dates}
    return (max(months) - min(months) + 1 - len(months)) if len(months) > 1 else 0


def get_day_of_month_consistency(all_transactions: list[Transaction]) -> float:
    """
    Calculate the consistency of the day of the month for transactions.
    """
    days = [parse_date(t.date).day for t in all_transactions]
    if not days:
        return 0.0
    most_common_day = max(set(days), key=days.count)
    return days.count(most_common_day) / len(days)


def get_median_interval(all_transactions: list[Transaction]) -> float:
    """Calculate the median gap (in days) between transactions."""
    gaps = get_transaction_gaps(all_transactions)
    return median(gaps) if gaps else 0.0


def is_known_recurring_company(transaction_name: str) -> bool:
    """
    Flags transactions as recurring if the company name contains specific keywords,
    regardless of price variation.
    """
    known_recurring_keywords = [
        "Amazon Prime",
        "American Water Works",
        "ancestry",
        "at&t",
        "canva",
        "comcast",
        "cox",
        "cricket wireless",
        "disney",
        "disney+",
        "energy",
        "geico",
        "google storage",
        "hulu",
        "HBO Max",
        "insurance",
        "mobile",
        "national grid",
        "netflix",
        "ngrid",
        "peacock",
        "Placer County Water Age",
        "spotify",
        "sezzle",
        "smyrna finance",
        "spectrum",
        "utility",
        "utilities",
        "verizon",
        "walmart+",
        "wireless",
        "wix",
        "youtube",
    ]

    transaction_name_lower = transaction_name.lower()
    return any(keyword in transaction_name_lower for keyword in known_recurring_keywords)


def is_known_fixed_subscription(transaction: Transaction) -> bool:
    """
    Flags transactions as recurring if the company name contains specific keywords
    and the amount matches a known subscription fee.
    """
    known_subscriptions = {
        "albert": [14.99],
        "ava finance": [9.0],
        "brigit": [8.99],
        "cleo": [5.99, 6.99],  # Consolidated Cleo variations
        "cleo ai": [5.99, 6.99],  # Cleo AI also has the same pricing
        "credit genie": [3.99, 4.99],
        "dave": [1.0],
        "empower": [8.0],
        "grid": [10.0],
    }

    transaction_name_lower = transaction.name.lower()
    return any(
        company in transaction_name_lower and any(abs(transaction.amount - amt) < 0.01 for amt in sub_amounts)
        for company, sub_amounts in known_subscriptions.items()
    )


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int | bool]:
    """
    Extract features for a transaction.
    This function assumes that transactions with the same name belong to the same recurring series.
    """
    relevant_transactions = [t for t in all_transactions if t.name == transaction.name]
    return {
        "amount": transaction.amount,
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        "n_transactions_same_name": len(relevant_transactions),
        "transaction_frequency": get_transaction_frequency(relevant_transactions),
        "transaction_std_amount": get_transaction_std_amount(relevant_transactions),
        "follows_regular_interval": follows_regular_interval(relevant_transactions),
        "skipped_months": detect_skipped_months(relevant_transactions),
        "day_of_month_consistency": get_day_of_month_consistency(relevant_transactions),
        "coefficient_of_variation": get_coefficient_of_variation(relevant_transactions),
        "median_interval": get_median_interval(relevant_transactions),
        "is_known_recurring_company": is_known_recurring_company(transaction.name),
        "is_known_fixed_subscription": is_known_fixed_subscription(transaction),
    }
