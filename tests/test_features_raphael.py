# test features_raphael.py


from recur_scan.features_raphael import (
    apple_transaction_amount_profile,  # <-- Add this import to fix the NameError
    get_amount_mad,  # <-- Added missing import
    get_amount_roundness,  # <-- Add this import
    get_amount_variation,
    get_description_pattern,
    get_has_irregular_spike,
    get_has_trial_period,
    get_is_common_subscription_amount,
    get_is_first_of_month,
    get_is_fixed_interval,
    get_is_recurring_charge,  # <-- Add this import to fix the NameError
    get_is_seasonal,
    get_is_similar_name,
    # New feature imports
    get_is_weekday_consistent,
    get_is_weekend_transaction,
    get_merchant_fingerprint,
    get_n_transactions_days_apart,
    get_n_transactions_same_day,
    get_new_features,
    get_occurs_same_week,
    get_pct_transactions_days_apart,
    get_pct_transactions_same_day,
    get_recurrence_confidence_score,  # <-- Added missing import
    get_recurring_confidence,  # <-- Fix: import the missing function
    get_transaction_trust_score,  # <-- Add this import
    get_vendor_risk_keywords,  # <-- Add this import to fix the NameError
    get_vendor_trust_score,  # <-- Add this import to fix the NameError
    is_apple_subscription_service,  # <-- Add this import to fix the NameError
)
from recur_scan.transactions import Transaction


# ===== Existing Test Cases (Unchanged) =====
def test_get_n_transactions_same_day() -> None:
    """Test that get_n_transactions_same_day returns the correct number of transactions on the same day."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),  # Same day
        Transaction(id=3, user_id="user1", name="Netflix", amount=15.99, date="2024-01-02"),  # +1 day
        Transaction(id=4, user_id="user1", name="Netflix", amount=15.99, date="2024-01-31"),  # Month boundary case
        Transaction(id=5, user_id="user1", name="Spotify", amount=9.99, date="2024-02-01"),
    ]

    # Exact same day matches (no tolerance)
    assert get_n_transactions_same_day(transactions[0], transactions, 0) == 2  # Only Jan 1 transactions

    # With 1 day tolerance
    assert get_n_transactions_same_day(transactions[0], transactions, 1) == 3  # Jan 1, Jan 2

    # Month boundary case with 1 day tolerance (Jan 31 and Feb 1)
    jan31 = Transaction(id=6, user_id="user1", name="Rent", amount=1200.0, date="2024-01-31")
    feb1 = Transaction(id=7, user_id="user1", name="Rent", amount=1200.0, date="2024-02-01")
    assert get_n_transactions_same_day(jan31, [jan31, feb1], 1) == 2


def test_get_pct_transactions_same_day() -> None:
    """Test that get_pct_transactions_same_day returns the correct percentage of transactions on the same day."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="Spotify", amount=9.99, date="2024-02-01"),
    ]
    assert get_pct_transactions_same_day(transactions[0], transactions, 0) == 2 / 3


def test_get_n_transactions_days_apart() -> None:
    """Test get_n_transactions_days_apart."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-01-31"),
        Transaction(id=3, user_id="user1", name="Spotify", amount=9.99, date="2024-02-01"),
    ]
    assert get_n_transactions_days_apart(transactions[0], transactions, 30, 0) == 1
    assert get_n_transactions_days_apart(transactions[0], transactions, 30, 1) == 2


def test_get_pct_transactions_days_apart() -> None:
    """Test get_pct_transactions_days_apart."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-01-31"),
        Transaction(id=3, user_id="user1", name="Spotify", amount=9.99, date="2024-02-01"),
    ]
    assert get_pct_transactions_days_apart(transactions[0], transactions, 30, 0) == 1 / 3
    assert get_pct_transactions_days_apart(transactions[0], transactions, 30, 1) == 2 / 3


def test_get_is_common_subscription_amount() -> None:
    """Test that get_is_common_subscription_amount correctly identifies subscription amounts."""
    assert get_is_common_subscription_amount(
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01")
    )
    assert not get_is_common_subscription_amount(
        Transaction(id=2, user_id="user1", name="Unknown Service", amount=27.5, date="2024-01-01")
    )


def test_get_is_first_of_month() -> None:
    """Test get_is_first_of_month."""
    assert get_is_first_of_month(Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"))
    assert not get_is_first_of_month(Transaction(id=2, user_id="user1", name="Spotify", amount=9.99, date="2024-01-15"))


def test_get_is_fixed_interval() -> None:
    """Test get_is_fixed_interval."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=15.99, date="2024-03-01"),
    ]
    assert get_is_fixed_interval(
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-03-01"), transactions
    )
    assert not get_is_fixed_interval(
        Transaction(id=2, user_id="user1", name="Spotify", amount=9.99, date="2024-01-15"), transactions
    )


def test_get_is_similar_name() -> None:
    """Test get_is_similar_name."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix Premium", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
    ]
    assert get_is_similar_name(transactions[0], transactions)
    assert not get_is_similar_name(
        Transaction(id=3, user_id="user1", name="Spotify", amount=9.99, date="2024-01-15"), transactions
    )


def test_get_has_irregular_spike() -> None:
    """Test get_has_irregular_spike."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-01-31"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=50.99, date="2024-02-01"),
    ]
    assert get_has_irregular_spike(
        Transaction(id=3, user_id="user1", name="Netflix", amount=150.99, date="2024-03-01"), transactions
    )
    assert not get_has_irregular_spike(
        Transaction(id=4, user_id="user1", name="Spotify", amount=9.99, date="2024-01-15"), transactions
    )


def test_get_occurs_same_week() -> None:
    """Test get_occurs_same_week."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Salary", amount=3000.0, date="2024-01-05"),  # First Friday
        Transaction(id=2, user_id="user1", name="Salary", amount=3000.0, date="2024-02-02"),  # First Friday
    ]
    assert get_occurs_same_week(
        Transaction(id=3, user_id="user1", name="Salary", amount=3000.0, date="2024-03-01"), transactions
    )
    assert not get_occurs_same_week(
        Transaction(id=4, user_id="user1", name="Bonus", amount=500.0, date="2024-01-15"), transactions
    )


# ===== New Test Cases for Additional Features =====
def test_get_is_weekday_consistent() -> None:
    """Test get_is_weekday_consistent."""
    # Monday transactions
    monday_txns = [
        Transaction(id=1, user_id="user1", name="Gym", amount=50.0, date="2024-01-01"),  # Monday
        Transaction(id=2, user_id="user1", name="Gym", amount=50.0, date="2024-01-08"),  # Monday
    ]
    # Mixed weekday transactions
    mixed_txns = [
        Transaction(id=3, user_id="user1", name="Yoga", amount=30.0, date="2024-01-01"),  # Monday
        Transaction(id=4, user_id="user1", name="Yoga", amount=30.0, date="2024-01-03"),  # Wednesday
    ]

    assert get_is_weekday_consistent(monday_txns[0], monday_txns)
    assert not get_is_weekday_consistent(mixed_txns[0], mixed_txns)


def test_get_is_seasonal() -> None:
    """Test get_is_seasonal."""
    annual_txns = [
        Transaction(id=1, user_id="user1", name="Insurance", amount=500.0, date="2023-01-15"),
        Transaction(id=2, user_id="user1", name="Insurance", amount=500.0, date="2024-01-16"),
    ]
    monthly_txns = [
        Transaction(id=3, user_id="user1", name="Rent", amount=1200.0, date="2024-01-01"),
        Transaction(id=4, user_id="user1", name="Rent", amount=1200.0, date="2024-02-01"),
    ]

    assert get_is_seasonal(annual_txns[1], annual_txns)
    assert not get_is_seasonal(monthly_txns[1], monthly_txns)


def test_get_amount_variation() -> None:
    """Test get_amount_variation."""
    stable_txns = [
        Transaction(id=1, user_id="user1", name="Utility", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Utility", amount=105.0, date="2024-02-01"),
    ]
    variable_txns = [
        Transaction(id=3, user_id="user1", name="Electric", amount=80.0, date="2024-01-01"),
        Transaction(id=4, user_id="user1", name="Electric", amount=120.0, date="2024-02-01"),
    ]

    assert 0 < get_amount_variation(stable_txns[0], stable_txns) < 10
    assert get_amount_variation(variable_txns[0], variable_txns) >= 20


def test_get_has_trial_period() -> None:
    """Test get_has_trial_period."""
    trial_txns = [
        Transaction(id=1, user_id="user1", name="Service", amount=0.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Service", amount=9.99, date="2024-02-01"),
    ]
    regular_txns = [
        Transaction(id=3, user_id="user1", name="Subscription", amount=9.99, date="2024-01-01"),
        Transaction(id=4, user_id="user1", name="Subscription", amount=9.99, date="2024-02-01"),
    ]

    assert get_has_trial_period(trial_txns[1], trial_txns)
    assert not get_has_trial_period(regular_txns[1], regular_txns)


def test_get_description_pattern() -> None:
    """Test get_description_pattern."""
    assert (
        get_description_pattern(Transaction(id=1, user_id="user1", name="ACH Payment", amount=100, date="2024-01-01"))
        == 1
    )
    assert (
        get_description_pattern(
            Transaction(id=2, user_id="user1", name="Autopay Electric", amount=100, date="2024-01-01")
        )
        == 2
    )
    assert (
        get_description_pattern(Transaction(id=3, user_id="user1", name="Invoice #123", amount=100, date="2024-01-01"))
        == 4
    )
    assert (
        get_description_pattern(Transaction(id=4, user_id="user1", name="Grocery Store", amount=50, date="2024-01-01"))
        == 0
    )


def test_get_is_weekend_transaction() -> None:
    """Test get_is_weekend_transaction."""
    assert get_is_weekend_transaction(
        Transaction(id=1, user_id="user1", name="Weekend", amount=50, date="2024-01-06")
    )  # Saturday
    assert not get_is_weekend_transaction(
        Transaction(id=2, user_id="user1", name="Weekday", amount=50, date="2024-01-01")
    )  # Monday


def test_get_merchant_fingerprint() -> None:
    """Test get_merchant_fingerprint with various transaction patterns."""
    # Test perfect recurring pattern (should score close to 1.0)
    recurring_txns = [
        Transaction(id=1, user_id="user1", name="NETFLIX AUTOPAY", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="NETFLIX AUTOPAY", amount=15.99, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="NETFLIX AUTOPAY", amount=15.99, date="2024-03-01"),
    ]
    recurring_score = get_merchant_fingerprint(recurring_txns[0], recurring_txns)
    assert 0.89 <= recurring_score <= 1.0, f"Expected score between 0.89 and 1.0, got {recurring_score}"

    # Test variable amounts (should score lower, e.g., 0.6-0.8)
    variable_txns = [
        Transaction(id=4, user_id="user1", name="AMAZON PRIME", amount=14.99, date="2024-01-15"),
        Transaction(id=5, user_id="user1", name="AMAZON PRIME", amount=12.99, date="2024-02-15"),
        Transaction(id=6, user_id="user1", name="AMAZON PRIME", amount=16.99, date="2024-03-15"),
    ]
    variable_score = get_merchant_fingerprint(variable_txns[0], variable_txns)
    assert 0.6 <= variable_score <= 0.89, f"Expected score between 0.6 and 0.89, got {variable_score}"

    # Test single transaction (should score 0.0)
    single_txn = [
        Transaction(id=7, user_id="user1", name="SINGLE PAYMENT", amount=100.0, date="2024-01-01"),
    ]
    single_score = get_merchant_fingerprint(single_txn[0], single_txn)
    assert single_score == 0.0, f"Expected score of 0.0, got {single_score}"


def test_get_recurrence_confidence_score() -> None:
    txns = [
        Transaction(id=1, user_id="u", name="GYM", amount=50, date="2024-01-01"),
        Transaction(id=2, user_id="u", name="GYM", amount=50, date="2024-02-01"),
    ]
    score = get_recurrence_confidence_score(txns[0], txns)
    assert 0 <= score <= 1
    # Perfect recurring should be high
    assert score > 0.7


def test_get_transaction_trust_score() -> None:
    txns = [
        Transaction(id=1, user_id="u", name="Netflix", amount=9.99, date="2024-01-01"),
        Transaction(id=2, user_id="u", name="Netflix", amount=9.99, date="2024-02-01"),
    ]
    score = get_transaction_trust_score(txns[0], txns)
    assert 0 <= score <= 1
    # Trusted merchant should have a reasonably high score
    assert score > 0.5


def test_recurring_confidence():
    # Perfect recurring (score ≈1.0)
    tx1 = Transaction(id=1, user_id="user1", name="NETFLIX AUTOPAY", amount=15.99, date="2024-01-01")
    tx2 = Transaction(id=2, user_id="user1", name="NETFLIX AUTOPAY", amount=15.99, date="2024-02-01")
    assert 0.98 <= get_recurring_confidence(tx1, [tx1, tx2]) <= 1.0

    # Natural variance (score ≈0.85)
    tx3 = Transaction(id=3, user_id="user1", name="GYM MEMBERSHIP", amount=50.0, date="2024-01-01")
    tx4 = Transaction(id=4, user_id="user1", name="GYM MEMBERSHIP", amount=52.0, date="2024-02-05")  # +5 days, +4%
    assert 0.8 <= get_recurring_confidence(tx3, [tx3, tx4]) <= 0.95

    # Non-recurring (score <0.3)
    tx5 = Transaction(id=5, user_id="user1", name="INVOICE #123", amount=100.0, date="2024-01-01")
    tx6 = Transaction(id=6, user_id="user1", name="INVOICE #123", amount=250.0, date="2024-06-01")
    assert get_recurring_confidence(tx5, [tx5, tx6]) < 0.3


def test_get_amount_mad():
    # Test 1: Single transaction
    t1 = Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2023-01-01")
    assert get_amount_mad(t1, [t1]) == 0.0

    # Test 2: Multiple identical transactions
    t2 = Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2023-01-02")
    t3 = Transaction(id=3, user_id="user1", name="Netflix", amount=15.99, date="2023-01-03")
    assert get_amount_mad(t1, [t1, t2, t3]) == 0.0

    # Test 3: Varied amounts
    t4 = Transaction(id=4, user_id="user1", name="Netflix", amount=14.99, date="2023-01-04")
    t5 = Transaction(id=5, user_id="user1", name="Netflix", amount=16.99, date="2023-01-05")
    result = get_amount_mad(t1, [t1, t4, t5])
    # Median = 15.99, deviations = [1.0, 0.0, 1.0], MAD = 1.0
    expected = (1.0 / 15.99) * 100
    assert abs(result - expected) < 0.001

    # Test 4: Zero amount handling
    t6 = Transaction(id=6, user_id="user1", name="Free", amount=0, date="2023-01-06")
    t7 = Transaction(id=7, user_id="user1", name="Free", amount=0, date="2023-01-07")
    assert get_amount_mad(t6, [t6, t7]) == 0.0


def test_get_vendor_risk_keywords():
    # Should detect risk keywords
    assert get_vendor_risk_keywords("Payday Loans") is True
    assert get_vendor_risk_keywords("Lending Club") is True
    # Should not detect risk keywords
    assert get_vendor_risk_keywords("Apple Store") is False
    # Custom keywords
    assert get_vendor_risk_keywords("FastAdvance", {"Advance"}) is True
    assert get_vendor_risk_keywords("SafeBank", {"Advance"}) is False


def test_amount_roundness():
    # Common subscription amounts
    assert get_amount_roundness(Transaction(id=1, user_id="user1", name="Sub", amount=9.99, date="2023-01-01")) == 1.0
    assert get_amount_roundness(Transaction(id=2, user_id="user1", name="Sub", amount=10.00, date="2023-01-01")) == 1.0
    assert get_amount_roundness(Transaction(id=3, user_id="user1", name="Sub", amount=19.95, date="2023-01-01")) == 0.5

    # Non-typical amounts
    assert get_amount_roundness(Transaction(id=4, user_id="user1", name="Sub", amount=9.97, date="2023-01-01")) == 0.0
    assert get_amount_roundness(Transaction(id=5, user_id="user1", name="Sub", amount=10.23, date="2023-01-01")) == 0.0


def test_vendor_trust_score():
    # Trusted vendors
    assert get_vendor_trust_score("Apple", {"Apple", "AT&T"}, {"AfterPay"}) == 1.0
    assert get_vendor_trust_score("AT&T", {"Apple", "AT&T"}, {"AfterPay"}) == 1.0

    # High-risk vendors
    assert get_vendor_trust_score("AfterPay", {"Apple"}, {"AfterPay", "CreditNinja"}) == 0.1
    assert get_vendor_trust_score("CreditNinja", {"Apple"}, {"AfterPay", "CreditNinja"}) == 0.1

    # Neutral vendors
    assert get_vendor_trust_score("Amazon", {"Apple"}, {"AfterPay"}) == 0.5
    assert get_vendor_trust_score("Netflix", {"Apple"}, {"AfterPay"}) == 0.5


def test_is_recurring_charge():
    # Recurring charges
    history = {"user1": [{"vendor": "Netflix", "days_ago": 15}, {"vendor": "Netflix", "days_ago": 10}]}
    assert get_is_recurring_charge("Netflix", "user1", history) is True

    # Non-recurring charges
    history = {"user2": [{"vendor": "Amazon", "days_ago": 40}]}
    assert get_is_recurring_charge("Amazon", "user2", history) is False

    # Edge case: exactly 30 days
    history = {"user3": [{"vendor": "Spotify", "days_ago": 30}, {"vendor": "Spotify", "days_ago": 29}]}
    assert get_is_recurring_charge("Spotify", "user3", history) is True


def test_is_apple_subscription_service():
    # Legitimate subscriptions
    assert is_apple_subscription_service("APPLE MUSIC") is True
    assert is_apple_subscription_service("iCloud 50GB Storage") is True

    # Non-subscription purchases
    assert is_apple_subscription_service("Apple Store Purchase") is False
    assert is_apple_subscription_service("Apple iPhone Case") is False


def test_apple_transaction_amount_profile():
    # Common subscription amounts
    assert apple_transaction_amount_profile(9.99) == 1.0
    assert apple_transaction_amount_profile(4.99) == 1.0

    # Suspicious amounts
    assert apple_transaction_amount_profile(100.00) == 0.0
    assert apple_transaction_amount_profile(37.42) == 0.0


def test_get_new_features() -> None:
    """Test get_new_features with validation for all features, including the new merchant_fingerprint."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=9.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=9.99, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="ACH Rent Payment", amount=1200.0, date="2024-01-01"),
        Transaction(id=4, user_id="user1", name="ACH Rent Payment", amount=1200.0, date="2024-02-01"),
        Transaction(id=5, user_id="user1", name="Trial Service", amount=0.0, date="2024-01-01"),
        Transaction(id=6, user_id="user1", name="Trial Service", amount=14.99, date="2024-02-01"),
    ]

    # Test Netflix transaction (monthly subscription)
    netflix_features = get_new_features(transactions[1], transactions)

    # Existing feature asserts
    assert "is_weekday_consistent" in netflix_features
    assert "is_seasonal" in netflix_features
    assert "amount_variation_pct" in netflix_features
    assert "had_trial_period" in netflix_features
    assert "description_pattern" in netflix_features
    assert "is_weekend_transaction" in netflix_features
    assert "n_days_apart_30" in netflix_features
    assert "pct_days_apart_30" in netflix_features

    # New merchant_fingerprint assert
    assert "merchant_fingerprint" in netflix_features, "Missing merchant_fingerprint feature"
    assert isinstance(netflix_features["merchant_fingerprint"], float), "Should return float score"
    assert 0 <= netflix_features["merchant_fingerprint"] <= 1, "Score should be 0-1"

    # Validate expected scores for different patterns
    netflix_score = netflix_features["merchant_fingerprint"]
    assert 0.89 <= netflix_score <= 1.0, f"Netflix should score 0.9-1.0 (got {netflix_score})"

    # Test ACH Rent (should score high due to consistent amount + ACH in name)
    rent_features = get_new_features(transactions[3], transactions)
    assert 0.95 <= float(rent_features["merchant_fingerprint"]) <= 1.0

    # Test Trial Service (lower score due to amount change)
    trial_features = get_new_features(transactions[5], transactions)
    assert 0.15 <= float(trial_features["merchant_fingerprint"]) <= 0.3
