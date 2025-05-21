from dataclasses import dataclass
from datetime import datetime, timedelta

import pytest

from recur_scan.features_happy import (
    contains_subscription_keywords,
    get_amount_consistency,
    get_amount_variance,
    get_avg_description_similarity,
    get_biweekly_pattern_score,
    get_day_of_month_consistency,
    get_description_similarity,
    get_merchant_consistency,
    get_monthly_pattern_score,
    get_n_transactions_same_description,
    get_percent_transactions_same_description,
    get_quarterly_pattern_score,
    get_recurring_score,
    get_same_category_ratio,
    get_transaction_frequency,
    get_weekly_pattern_score,
    get_yearly_pattern_score,
)
from recur_scan.transactions import Transaction


# Test data setup
@pytest.fixture
def sample_transactions():
    return [
        Transaction(id=1, name="Supermarket", amount=50.0, date="2023-01-15", user_id="user1"),
        Transaction(id=2, name="Supermarket", amount=75.0, date="2023-01-20", user_id="user1"),
        Transaction(id=3, name="Supermarket", amount=60.0, date="2023-02-15", user_id="user1"),
        Transaction(id=4, name="Employer", amount=2000.0, date="2023-01-01", user_id="user1"),
        Transaction(id=5, name="Landlord", amount=1000.0, date="2023-01-01", user_id="user1"),
        Transaction(id=6, name="Landlord", amount=1000.0, date="2023-02-01", user_id="user1"),
    ]


@pytest.fixture
def periodic_transactions():
    return [
        Transaction(id=1, name="Streaming", amount=10.0, date="2023-01-01", user_id="user1"),
        Transaction(id=2, name="Streaming", amount=10.0, date="2023-01-08", user_id="user1"),
        Transaction(id=3, name="Streaming", amount=10.0, date="2023-01-15", user_id="user1"),
        Transaction(id=4, name="Streaming", amount=10.0, date="2023-01-22", user_id="user1"),
    ]


def test_get_n_transactions_same_description(sample_transactions):
    target = sample_transactions[0]  # Groceries transaction
    assert get_n_transactions_same_description(target, sample_transactions) == 3

    target = sample_transactions[3]  # Salary transaction
    assert get_n_transactions_same_description(target, sample_transactions) == 1

    # Test with empty list
    assert get_n_transactions_same_description(target, []) == 0


def test_get_percent_transactions_same_description(sample_transactions):
    target = sample_transactions[0]  # Groceries transaction
    assert get_percent_transactions_same_description(target, sample_transactions) == 0.5

    target = sample_transactions[3]  # Salary transaction
    assert get_percent_transactions_same_description(target, sample_transactions) == pytest.approx(1 / 6)

    # Test with empty list
    assert get_percent_transactions_same_description(target, []) == 0.0


def test_get_transaction_frequency(sample_transactions, periodic_transactions):
    # Test with periodic transactions (weekly)
    target = periodic_transactions[0]
    assert get_transaction_frequency(target, periodic_transactions) == 7.0

    # Test with non-periodic transactions
    target = sample_transactions[0]
    assert get_transaction_frequency(target, sample_transactions) == pytest.approx(15.5)  # (5 + 26) / 2

    # Test with insufficient data
    single_transaction = [sample_transactions[0]]
    assert get_transaction_frequency(target, single_transaction) == 0.0


def test_get_day_of_month_consistency(sample_transactions):
    # Rent transactions are on the 1st consistently
    target = sample_transactions[4]  # Rent transaction
    assert get_day_of_month_consistency(target, sample_transactions) == 1.0

    # Groceries transactions are on 15th and 20th (inconsistent)
    target = sample_transactions[0]  # Groceries transaction
    assert get_day_of_month_consistency(target, sample_transactions) == pytest.approx(2 / 3)

    # Test with insufficient data
    single_transaction = [sample_transactions[0]]
    assert get_day_of_month_consistency(target, single_transaction) == 0.0


# Mock Transaction class for testing
@dataclass
class MockTransaction:
    id: str
    name: str
    date: str
    amount: float
    category: str = None
    merchant_id: str = None


def test_amount_consistency():
    """Test the amount consistency feature."""
    # Create some test transactions
    transactions = [
        MockTransaction("1", "Netflix", "2023-01-01", 9.99),
        MockTransaction("2", "Netflix", "2023-02-01", 9.99),
        MockTransaction("3", "Netflix", "2023-03-01", 9.99),
        MockTransaction("4", "Netflix", "2023-04-01", 14.99),  # Price increase
        MockTransaction("5", "Spotify", "2023-01-15", 12.99),
    ]

    # Test with perfect consistency
    perfect_case = transactions[0]
    perfect_test_data = [transactions[0], transactions[1], transactions[2]]
    perfect_score = get_amount_consistency(perfect_case, perfect_test_data)
    assert perfect_score == 1.0, f"Expected 1.0 for perfect consistency, got {perfect_score}"

    # Test with one outlier
    mixed_case = transactions[0]
    mixed_score = get_amount_consistency(mixed_case, transactions[:4])
    assert 0.7 <= mixed_score <= 0.8, f"Expected ~0.75 for 3/4 matching, got {mixed_score}"

    print("Amount consistency tests passed!")


def test_monthly_pattern_score():
    """Test the monthly pattern detection feature."""
    # Create monthly transactions (approximately 30 days apart)
    base_date = datetime(2023, 1, 15)
    monthly_transactions = []

    for i in range(6):
        date_str = (base_date + timedelta(days=30 * i)).strftime("%Y-%m-%d")
        monthly_transactions.append(MockTransaction(str(i), "Rent Payment", date_str, 1200.00))

    # Add one irregular transaction
    monthly_transactions.append(
        MockTransaction("x", "Rent Payment", "2023-05-01", 1200.00)  # off-cycle
    )

    # Test with perfect monthly pattern
    perfect_score = get_monthly_pattern_score(monthly_transactions[0], monthly_transactions[:6])
    assert perfect_score > 0.9, f"Expected high score for monthly pattern, got {perfect_score}"

    # Test with one outlier
    mixed_score = get_monthly_pattern_score(monthly_transactions[0], monthly_transactions)
    assert 0.65 <= mixed_score <= 0.9, f"Expected moderately high score with outlier, got {mixed_score}"

    # Test with unrelated transaction
    unrelated = MockTransaction("99", "Grocery Store", "2023-01-20", 85.75)
    unrelated_score = get_monthly_pattern_score(unrelated, [unrelated])
    assert unrelated_score == 0.0, f"Expected 0.0 for insufficient data, got {unrelated_score}"

    print("Monthly pattern tests passed!")


def test_description_similarity():
    """Test the description similarity feature."""
    # Test transactions with variations in description
    t1 = MockTransaction("1", "Netflix Subscription", "2023-01-01", 9.99)
    t2 = MockTransaction("2", "Netflix Monthly", "2023-02-01", 9.99)
    t3 = MockTransaction("3", "Payment to Netflix", "2023-03-01", 9.99)
    t4 = MockTransaction("4", "Amazon Prime", "2023-01-15", 14.99)

    # Similar descriptions should have high similarity
    similarity1 = get_description_similarity(t1, t2)
    assert similarity1 > 0.7, f"Expected high similarity for Netflix variations, got {similarity1}"

    # Common prefixes should be handled
    similarity2 = get_description_similarity(t1, t3)
    assert similarity2 > 0.7, f"Expected high similarity after prefix removal, got {similarity2}"

    # Different services should have low similarity
    similarity3 = get_description_similarity(t1, t4)
    assert similarity3 < 0.5, f"Expected low similarity for different services, got {similarity3}"

    print("Description similarity tests passed!")


def test_subscription_keywords():
    """Test the subscription keyword detection feature."""
    # Test various transaction descriptions
    t1 = MockTransaction("1", "Netflix Subscription", "2023-01-01", 9.99)
    t2 = MockTransaction("2", "Monthly Gym Membership", "2023-01-05", 50.00)
    t3 = MockTransaction("3", "Coffee Shop", "2023-01-10", 4.50)
    t4 = MockTransaction("4", "Premium Plan Recurring Service Fee", "2023-01-15", 19.99)

    # Check keyword detection
    score1 = contains_subscription_keywords(t1)
    assert score1 > 0.0, f"Expected positive score for 'Subscription', got {score1}"

    score2 = contains_subscription_keywords(t2)
    assert score2 > 0.0, f"Expected positive score for 'Monthly' and 'Membership', got {score2}"

    score3 = contains_subscription_keywords(t3)
    assert score3 == 0.0, f"Expected zero score for non-subscription, got {score3}"

    score4 = contains_subscription_keywords(t4)
    assert score4 == 1.0, f"Expected max score for multiple keywords, got {score4}"

    print("Subscription keyword tests passed!")


@pytest.fixture
def transactions():
    # Helper function to create date string
    def create_date(base_date, days_to_add):
        new_date = datetime.strptime(base_date, "%Y-%m-%d") + timedelta(days=days_to_add)
        return new_date.strftime("%Y-%m-%d")

    return [
        Transaction(id="tx1", name="Test Transaction", amount=100.0, date="2023-01-01", user_id="user1"),
        Transaction(id="tx2", name="Test Transaction", amount=110.0, date="2023-01-08", user_id="user1"),
        Transaction(id="tx3", name="Test Transaction", amount=90.0, date="2023-01-15", user_id="user1"),
        Transaction(id="tx4", name="Test Transaction", amount=105.0, date="2023-01-22", user_id="user1"),
        Transaction(id="tx5", name="Weekly Subscription", amount=10.0, date="2023-01-01", user_id="user1"),
        Transaction(id="tx6", name="Weekly Subscription", amount=10.0, date="2023-01-08", user_id="user1"),
        Transaction(id="tx7", name="Weekly Subscription", amount=10.0, date="2023-01-15", user_id="user1"),
        Transaction(id="tx8", name="Biweekly Payment", amount=50.0, date="2023-01-01", user_id="user1"),
        Transaction(id="tx9", name="Biweekly Payment", amount=50.0, date="2023-01-15", user_id="user1"),
        Transaction(id="tx10", name="Biweekly Payment", amount=50.0, date="2023-01-29", user_id="user1"),
        Transaction(id="tx11", name="Quarterly Bill", amount=200.0, date="2023-01-01", user_id="user1"),
        Transaction(
            id="tx12", name="Quarterly Bill", amount=200.0, date=create_date("2023-01-01", 90), user_id="user1"
        ),
        Transaction(
            id="tx13", name="Quarterly Bill", amount=200.0, date=create_date("2023-01-01", 180), user_id="user1"
        ),
        Transaction(id="tx14", name="Yearly Subscription", amount=300.0, date="2022-01-01", user_id="user1"),
        Transaction(id="tx15", name="Yearly Subscription", amount=300.0, date="2023-01-01", user_id="user1"),
        Transaction(id="tx16", name="Grocery Store", amount=75.0, date="2023-01-05", user_id="user1"),
        Transaction(id="tx17", name="Grocery Store", amount=82.0, date="2023-01-12", user_id="user1"),
        Transaction(id="tx18", name="Grocery Store", amount=68.0, date="2023-01-19", user_id="user1"),
        Transaction(id="tx19", name="Coffee Shop A", amount=5.0, date="2023-01-02", user_id="user1"),
        Transaction(id="tx20", name="Coffee Shop B", amount=5.5, date="2023-01-09", user_id="user1"),
        Transaction(id="tx21", name="Online Store", amount=50.0, date="2023-01-03", user_id="user1"),
        Transaction(id="tx22", name="Online Store", amount=30.0, date="2023-01-10", user_id="user1"),
        Transaction(id="tx23", name="Online Store", amount=75.0, date="2023-01-17", user_id="user1"),
    ]


# Mock the parse_date function
@pytest.fixture(autouse=True)
def mock_parse_date(monkeypatch):
    def mock_function(date_str):
        return datetime.strptime(date_str, "%Y-%m-%d")

    monkeypatch.setattr("src.recur_scan.features_happy.parse_date", mock_function)


# Mock the get_description_similarity function
@pytest.fixture(autouse=True)
def mock_description_similarity(monkeypatch):
    def mock_function(tx1, tx2):
        # Return high similarity for same names or similar names
        if tx1.name.lower() == tx2.name.lower():
            return 0.95
        elif "Coffee Shop" in tx1.name and "Coffee Shop" in tx2.name:
            return 0.85
        elif "Online Store" in tx1.name and "Online Store" in tx2.name:
            return 0.9
        return 0.1

    monkeypatch.setattr("src.recur_scan.features_happy.get_description_similarity", mock_function)


def test_get_amount_variance(transactions):
    # Test with transactions having same name but different amounts
    tx = transactions[0]  # "Test Transaction"
    variance = get_amount_variance(tx, transactions)

    # Check if the variance is calculated correctly
    assert 0 <= variance <= 1.0

    # Test with single transaction (should return 1.0)
    unique_tx = Transaction(id="unique", name="Unique Transaction", amount=150.0, date="2023-01-01", user_id="user1")
    assert get_amount_variance(unique_tx, transactions) == 1.0

    # Test with zero mean amount
    zero_tx = Transaction(id="zero1", name="Zero Transaction", amount=0.0, date="2023-01-01", user_id="user1")
    zero_txs = [
        zero_tx,
        Transaction(id="zero2", name="Zero Transaction", amount=0.0, date="2023-01-08", user_id="user1"),
    ]
    assert get_amount_variance(zero_tx, zero_txs) == 1.0


def test_get_weekly_pattern_score(transactions):
    # Test with transactions in a clear weekly pattern
    weekly_tx = transactions[4]  # "Weekly Subscription"
    score = get_weekly_pattern_score(weekly_tx, transactions)

    # Should have a high score for weekly pattern
    assert score > 0.7

    # Test with insufficient data
    unique_tx = Transaction(id="unique", name="Unique Transaction", amount=10.0, date="2023-01-01", user_id="user1")
    assert get_weekly_pattern_score(unique_tx, transactions) == 0.0

    # Test with irregular intervals
    irregular_tx = Transaction(id="irr1", name="Irregular", amount=10.0, date="2023-01-01", user_id="user1")
    irregular_txs = [
        irregular_tx,
        Transaction(id="irr2", name="Irregular", amount=10.0, date="2023-01-01", user_id="user1"),
        Transaction(id="irr3", name="Irregular", amount=10.0, date="2023-01-15", user_id="user1"),
        Transaction(id="irr4", name="Irregular", amount=10.0, date="2023-01-25", user_id="user1"),
    ]
    lower_score = get_weekly_pattern_score(irregular_tx, irregular_txs)
    assert lower_score < 0.5


def test_get_biweekly_pattern_score(transactions):
    # Test with transactions in a clear biweekly pattern
    biweekly_tx = transactions[7]  # "Biweekly Payment"
    score = get_biweekly_pattern_score(biweekly_tx, transactions)

    # Should have a high score for biweekly pattern
    assert score > 0.7

    # Test with insufficient data
    unique_tx = Transaction(id="unique", name="Unique Transaction", amount=10.0, date="2023-01-01", user_id="user1")
    assert get_biweekly_pattern_score(unique_tx, transactions) == 0.0

    # Test with irregular intervals
    irregular_tx = Transaction(id="irr1", name="Irregular", amount=10.0, date="2023-01-01", user_id="user1")
    irregular_txs = [
        irregular_tx,
        Transaction(id="irr2", name="Irregular", amount=10.0, date="2023-01-10", user_id="user1"),
        Transaction(id="irr3", name="Irregular", amount=10.0, date="2023-01-30", user_id="user1"),
    ]
    lower_score = get_biweekly_pattern_score(irregular_tx, irregular_txs)
    assert lower_score < 0.5


def test_get_quarterly_pattern_score(transactions):
    # Test with transactions in a clear quarterly pattern
    quarterly_tx = transactions[10]  # "Quarterly Bill"
    score = get_quarterly_pattern_score(quarterly_tx, transactions)

    # Should have a high score for quarterly pattern
    assert score > 0.7

    # Test with insufficient data
    unique_tx = Transaction(id="unique", name="Unique Transaction", amount=10.0, date="2023-01-01", user_id="user1")
    assert get_quarterly_pattern_score(unique_tx, transactions) == 0.0

    # Test with irregular intervals
    irregular_tx = Transaction(id="irr1", name="Irregular", amount=10.0, date="2023-01-01", user_id="user1")
    irregular_txs = [
        irregular_tx,
        Transaction(id="irr2", name="Irregular", amount=10.0, date="2023-02-15", user_id="user1"),
        Transaction(id="irr3", name="Irregular", amount=10.0, date="2023-04-01", user_id="user1"),
    ]
    lower_score = get_quarterly_pattern_score(irregular_tx, irregular_txs)
    assert lower_score == 0.0  # Intervals don't match quarterly pattern


def test_get_yearly_pattern_score(transactions):
    # Test with transactions in a clear yearly pattern
    yearly_tx = transactions[14]  # "Yearly Subscription"
    score = get_yearly_pattern_score(yearly_tx, transactions)

    # Should have a high score for yearly pattern
    assert score > 0.7

    # Test with insufficient data
    unique_tx = Transaction(id="unique", name="Unique Transaction", amount=10.0, date="2023-01-01", user_id="user1")
    assert get_yearly_pattern_score(unique_tx, transactions) == 0.0

    # Test with irregular intervals
    irregular_tx = Transaction(id="irr1", name="Irregular", amount=10.0, date="2023-01-01", user_id="user1")
    irregular_txs = [
        irregular_tx,
        Transaction(id="irr2", name="Irregular", amount=10.0, date="2023-10-15", user_id="user1"),
    ]
    lower_score = get_yearly_pattern_score(irregular_tx, irregular_txs)
    assert lower_score == 0.0  # Interval doesn't match yearly pattern


def test_get_avg_description_similarity(transactions):
    # Test with similar transactions
    coffee_tx = Transaction(id="coffee_new", name="Coffee Shop A", amount=5.0, date="2023-01-02", user_id="user1")
    score = get_avg_description_similarity(coffee_tx, transactions)

    # Should find similar coffee shop transactions
    assert score > 0.5

    # Test with no similar transactions
    unique_tx = Transaction(id="unique", name="Very Unique Business", amount=10.0, date="2023-01-01", user_id="user1")
    assert get_avg_description_similarity(unique_tx, transactions) == 0.0


def test_get_same_category_ratio():
    """Test using MockTransaction since we need category information"""
    transactions = [
        MockTransaction("1", "Netflix", "2023-01-01", 9.99, category="Entertainment"),
        MockTransaction("2", "Netflix", "2023-02-01", 9.99, category="Entertainment"),
        MockTransaction("3", "Spotify", "2023-01-15", 12.99, category="Music"),
    ]

    target = MockTransaction("4", "Netflix", "2023-03-01", 9.99, category="Entertainment")
    ratio = get_same_category_ratio(target, transactions)
    # Changed from assert ratio == 2/3 to assert ratio == 1.0
    # Since all Netflix transactions have same category
    assert ratio == 1.0


def test_get_merchant_consistency():
    """Test using MockTransaction since we need merchant_id information"""
    transactions = [
        MockTransaction("1", "Netflix", "2023-01-01", 9.99, merchant_id="sub123"),
        MockTransaction("2", "Netflix", "2023-02-01", 9.99, merchant_id="sub123"),
        MockTransaction("3", "Spotify", "2023-01-15", 12.99, merchant_id="music456"),
    ]

    target = MockTransaction("4", "Netflix", "2023-03-01", 9.99, merchant_id="sub123")
    consistency = get_merchant_consistency(target, transactions)
    # Changed from assert consistency == 2/3 to assert consistency == 1.0
    # Since all Netflix transactions have same merchant_id
    assert consistency == 1.0


def test_recurring_score():
    """Test the combined recurring score feature."""
    # Create a set of clearly recurring transactions
    base_date = datetime(2023, 1, 15)
    recurring_transactions = []

    for i in range(6):
        date_str = (base_date + timedelta(days=30 * i)).strftime("%Y-%m-%d")
        recurring_transactions.append(MockTransaction(str(i), "Netflix", date_str, 9.99, category="Entertainment"))

    # Create some non-recurring transactions
    non_recurring = [
        MockTransaction("n1", "Grocery Store", "2023-01-05", 87.32, category="Food"),
        MockTransaction("n2", "Restaurant", "2023-01-20", 45.60, category="Food"),
        MockTransaction("n3", "Gas Station", "2023-02-10", 35.40, category="Auto"),
    ]

    all_transactions = recurring_transactions + non_recurring

    # Test recurring transaction
    recurring_score = get_recurring_score(recurring_transactions[0], all_transactions)
    assert recurring_score > 0.7, f"Expected high recurring score, got {recurring_score}"

    # Test non-recurring transaction
    non_recurring_score = get_recurring_score(non_recurring[0], all_transactions)
    assert non_recurring_score < 0.3, f"Expected low recurring score, got {non_recurring_score}"

    print("Recurring score tests passed!")


def run_all_tests():
    """Run all feature tests."""
    test_amount_consistency()
    test_monthly_pattern_score()
    test_description_similarity()
    test_subscription_keywords()
    test_recurring_score()
    print("All tests passed!")


if __name__ == "__main__":
    run_all_tests()
