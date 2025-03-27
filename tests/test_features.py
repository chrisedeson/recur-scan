# test features
import pytest

from recur_scan.features import (
    detect_skipped_months,
    follows_regular_interval,
    get_coefficient_of_variation,
    get_day_of_month_consistency,
    get_ends_in_99,
    get_is_always_recurring,
    get_is_insurance,
    get_is_phone,
    get_is_utility,
    get_median_interval,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    # Christopher's functions
    get_n_transactions_same_amount_chris,
    get_n_transactions_same_day,
    get_n_transactions_same_name,
    get_pct_transactions_days_apart,
    get_pct_transactions_same_day,
    get_percent_transactions_same_amount,
    get_percent_transactions_same_amount_chris,
    get_transaction_frequency,
    get_transaction_gaps,
    get_transaction_std_amount,
    is_known_fixed_subscription,
    is_known_recurring_company,
)
from recur_scan.transactions import Transaction


def test_get_n_transactions_same_amount() -> None:
    """Test that get_n_transactions_same_amount returns the correct number of transactions with the same amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert get_n_transactions_same_amount(transactions[0], transactions) == 2
    assert get_n_transactions_same_amount(transactions[2], transactions) == 1


def test_get_percent_transactions_same_amount() -> None:
    """
    Test that get_percent_transactions_same_amount returns correct percentage.
    Tests that the function calculates the right percentage of transactions with matching amounts.
    """
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert pytest.approx(get_percent_transactions_same_amount(transactions[0], transactions)) == 2 / 4


def test_get_ends_in_99() -> None:
    """Test that get_ends_in_99 returns True for amounts ending in 99."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert not get_ends_in_99(transactions[0])
    assert get_ends_in_99(transactions[3])


def test_get_n_transactions_same_day() -> None:
    """Test that get_n_transactions_same_day returns the correct number of transactions on the same day."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert get_n_transactions_same_day(transactions[0], transactions, 0) == 2
    assert get_n_transactions_same_day(transactions[0], transactions, 1) == 3
    assert get_n_transactions_same_day(transactions[2], transactions, 0) == 1


def test_get_pct_transactions_same_day() -> None:
    """Test that get_pct_transactions_same_day returns the correct percentage of transactions on the same day."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert get_pct_transactions_same_day(transactions[0], transactions, 0) == 2 / 4


def test_get_n_transactions_days_apart() -> None:
    """Test get_n_transactions_days_apart."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-16"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-29"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-31"),
    ]
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 0) == 2
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 1) == 4


def test_get_pct_transactions_days_apart() -> None:
    """Test get_pct_transactions_days_apart."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-16"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-29"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-31"),
    ]
    assert get_pct_transactions_days_apart(transactions[0], transactions, 14, 0) == 2 / 7
    assert get_pct_transactions_days_apart(transactions[0], transactions, 14, 1) == 4 / 7


def test_get_is_insurance() -> None:
    """Test get_is_insurance."""
    assert get_is_insurance(
        Transaction(id=1, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-01")
    )
    assert not get_is_insurance(Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"))


def test_get_is_phone() -> None:
    """Test get_is_phone."""
    assert get_is_phone(Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"))
    assert not get_is_phone(Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"))


def test_get_is_utility() -> None:
    """Test get_is_utility."""
    assert get_is_utility(Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"))
    assert not get_is_utility(
        Transaction(id=4, user_id="user1", name="HighEnergy Soft Drinks", amount=2.99, date="2024-01-03")
    )


def test_get_is_always_recurring() -> None:
    """Test get_is_always_recurring."""
    assert get_is_always_recurring(Transaction(id=1, user_id="user1", name="netflix", amount=100, date="2024-01-01"))
    assert not get_is_always_recurring(
        Transaction(id=2, user_id="user1", name="walmart", amount=100, date="2024-01-01")
    )


##############################################################################
# Additional tests for Christopher's Features
##############################################################################


def test_get_n_transactions_same_amount_chris() -> None:
    """Test get_n_transactions_same_amount_chris with tolerance logic."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        # Within 1% tolerance (tol = 1.0)
        Transaction(id=2, user_id="user1", name="name1", amount=100.5, date="2024-01-01"),
        # Outside tolerance
        Transaction(id=3, user_id="user1", name="name1", amount=102, date="2024-01-02"),
    ]
    # For transaction 1, only transaction 2 is within tolerance.
    assert get_n_transactions_same_amount_chris(transactions[0], transactions) == 2
    # For transaction 2, transaction 1 and itself count.
    assert get_n_transactions_same_amount_chris(transactions[1], transactions) == 2


def test_get_percent_transactions_same_amount_chris() -> None:
    """Test get_percent_transactions_same_amount_chris returns the correct percentage."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100.5, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=102, date="2024-01-02"),
    ]
    count = get_n_transactions_same_amount_chris(transactions[0], transactions)
    expected = count / len(transactions)
    assert pytest.approx(get_percent_transactions_same_amount_chris(transactions[0], transactions)) == expected


def test_get_n_transactions_same_name() -> None:
    """Test get_n_transactions_same_name returns the correct count."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Store A", amount=50, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Store A", amount=75, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="Store B", amount=50, date="2024-01-03"),
    ]
    assert get_n_transactions_same_name(transactions[0], transactions) == 2
    assert get_n_transactions_same_name(transactions[2], transactions) == 1


def test_get_transaction_gaps() -> None:
    """Test get_transaction_gaps with valid and invalid inputs."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Store A", amount=50, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Store A", amount=50, date="2024-01-10"),
        Transaction(id=3, user_id="user1", name="Store A", amount=50, date="2024-01-20"),
    ]
    assert get_transaction_gaps(transactions) == [9, 10]
    assert get_transaction_gaps([]) == []


def test_get_transaction_frequency() -> None:
    """Test get_transaction_frequency with valid and invalid inputs."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Store A", amount=50, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Store A", amount=50, date="2024-01-10"),
        Transaction(id=3, user_id="user1", name="Store A", amount=50, date="2024-01-20"),
    ]
    assert pytest.approx(get_transaction_frequency(transactions)) == 9.5
    assert get_transaction_frequency([]) == 0.0


def test_get_transaction_std_amount() -> None:
    """Test get_transaction_std_amount with valid and invalid inputs."""
    # Sample transactions for valid input
    transactions = [
        Transaction(id=1, user_id="user1", name="Store A", amount=50, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Store A", amount=70, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="Store A", amount=90, date="2024-01-03"),
    ]

    # Test with valid transactions, should return standard deviation > 0
    std_amount = get_transaction_std_amount(transactions)
    assert std_amount > 0

    # Test with an empty list, should return 0.0
    assert get_transaction_std_amount([]) == 0.0

    # Test with all same amounts (no variation), should return 0.0
    transactions_same = [
        Transaction(id=1, user_id="user1", name="Store A", amount=50, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Store A", amount=50, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="Store A", amount=50, date="2024-01-03"),
    ]
    assert get_transaction_std_amount(transactions_same) == 0.0


def test_get_coefficient_of_variation() -> None:
    """Test get_coefficient_of_variation with valid and invalid inputs."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Store A", amount=50, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Store A", amount=70, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="Store A", amount=90, date="2024-01-03"),
    ]

    # Test with valid transactions, should return coefficient of variation > 0
    cv = get_coefficient_of_variation(transactions)
    assert cv > 0

    # Test with an empty list, should return 0.0
    assert get_coefficient_of_variation([]) == 0.0

    # Test with all same amounts (no variation), should return 0.0 for coefficient of variation
    transactions_same = [
        Transaction(id=1, user_id="user1", name="Store A", amount=50, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Store A", amount=50, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="Store A", amount=50, date="2024-01-03"),
    ]
    assert get_coefficient_of_variation(transactions_same) == 0.0


def test_follows_regular_interval() -> None:
    """Test follows_regular_interval with valid and invalid inputs."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Store A", amount=50, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Store A", amount=50, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Store A", amount=50, date="2024-03-01"),
    ]
    assert follows_regular_interval(transactions)
    assert not follows_regular_interval([])


def test_detect_skipped_months() -> None:
    """Test detect_skipped_months with valid and invalid inputs."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Store A", amount=50, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Store A", amount=50, date="2024-03-01"),
        Transaction(id=3, user_id="user1", name="Store A", amount=50, date="2024-04-01"),
    ]
    assert detect_skipped_months(transactions) == 1
    assert detect_skipped_months([]) == 0


def test_get_day_of_month_consistency() -> None:
    """Test get_day_of_month_consistency with valid and invalid inputs."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Store A", amount=50, date="2024-01-15"),
        Transaction(id=2, user_id="user1", name="Store A", amount=60, date="2024-02-15"),
        Transaction(id=3, user_id="user1", name="Store A", amount=70, date="2024-03-15"),
    ]
    assert get_day_of_month_consistency(transactions) == 1.0
    assert get_day_of_month_consistency([]) == 0.0


def test_get_median_interval() -> None:
    """Test get_median_interval with valid and invalid inputs."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Store A", amount=50, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Store A", amount=50, date="2024-01-04"),
        Transaction(id=3, user_id="user1", name="Store A", amount=50, date="2024-01-10"),
    ]
    assert pytest.approx(get_median_interval(transactions), 0.1) == 4.5
    assert get_median_interval([]) == 0.0


def test_is_known_recurring_company() -> None:
    """Test is_known_recurring_company with valid and invalid inputs."""
    assert is_known_recurring_company("Netflix")
    assert is_known_recurring_company("Hulu")
    assert not is_known_recurring_company("Local Grocery")


def test_is_known_fixed_subscription() -> None:
    """Test is_known_fixed_subscription with valid and invalid inputs."""
    assert is_known_fixed_subscription(Transaction(id=1, user_id="user1", name="Cleo", amount=5.99, date="2024-01-01"))
    assert not is_known_fixed_subscription(
        Transaction(id=2, user_id="user1", name="Local Gym", amount=30, date="2024-01-01")
    )
