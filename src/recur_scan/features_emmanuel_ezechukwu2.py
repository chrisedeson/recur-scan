from datetime import datetime
from statistics import mean, stdev

from fuzzywuzzy import process

from recur_scan.transactions import Transaction

RECURRING_VENDORS = {
    # Streaming & Entertainment
    "netflix",
    "spotify",
    "disney+",
    "hulu",
    "amazon prime",
    "hbo max",
    "apple music",
    "youtube premium",
    "paramount+",
    "peacock",
    # Cloud & Software Subscriptions
    "microsoft",
    "adobe",
    "google workspace",
    "dropbox",
    "zoom",
    "notion",
    "evernote",
    "github",
    "figma",
    "canva",
    "grammarly",
    # Telecom & Internet
    "at&t",
    "verizon",
    "t-mobile",
    "spectrum",
    "xfinity",
    "comcast",
    "google fi",
    "mint mobile",
    "cricket wireless",
    # Insurance & Financial Services
    "geico",
    "state farm",
    "progressive",
    "allstate",
    "hugo insurance",
    "metlife",
    "blue cross blue shield",
    "aetna",
    "cigna",
    # Utilities & Home Services
    "duke energy",
    "pg&e",
    "con edison",
    "national grid",
    "directv",
    "dish network",
    "ring",
    "adt security",
    "vivint",
    # Fitness & Health
    "planet fitness",
    "24 hour fitness",
    "la fitness",
    "peloton",
    "fitbit premium",
    "calm",
    "headspace",
    "myfitnesspal",
    # Food & Delivery
    "hello fresh",
    "blue apron",
    "doordash pass",
    "uber eats pass",
    "instacart+",
    "starbucks rewards",
    # Miscellaneous Subscriptions
    "amazon aws",
    "patreon",
    "onlyfans",
    "substack",
    "new york times",
    "washington post",
    "the economist",
    "linkedin premium",
    "audible",
}


def count_transactions_by_amount(transaction: Transaction, transactions: list[Transaction]) -> tuple[int, float]:
    """Returns count and percentage of transactions with the same amount."""
    if not transactions:
        return 0, 0.0
    same_amount_count = sum(1 for t in transactions if t.amount == transaction.amount)
    return same_amount_count, same_amount_count / len(transactions)


def get_recurrence_patterns(transaction: Transaction, transactions: list[Transaction]) -> dict:
    """Determines time-based recurrence patterns from past transactions."""
    merchant_txns = [t for t in transactions if t.name == transaction.name]

    if len(merchant_txns) < 2:
        return {
            key: 0
            for key in [
                # "is_biweekly_emmanuel2",
                # "is_semimonthly_emmanuel2",
                # "is_monthly_emmanuel2",
                # "is_bimonthly_emmanuel2",
                # "is_quarterly_emmanuel2",
                # "is_annual_emmanuel2",
                # "avg_days_between_emmanuel2",
                # "std_days_between_emmanuel2",
                "recurrence_score_emmanuel2",
            ]
        }

    dates = sorted(datetime.strptime(t.date, "%Y-%m-%d") for t in merchant_txns)
    date_diffs = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]

    avg_days_between = mean(date_diffs)
    # std_days_between = stdev(date_diffs) if len(date_diffs) > 1 else 0.0

    # Weighted recurrence score
    recurrence_score = sum(1 / (1 + abs(diff - avg_days_between)) for diff in date_diffs) / len(date_diffs)

    # recurrence_flags = {
    # "is_biweekly_emmanuel2": int(14 in date_diffs),
    # "is_semimonthly_emmanuel2": int(any(d in {14, 15, 16, 17} for d in date_diffs)),
    # "is_monthly_emmanuel2": int(any(27 <= d <= 31 for d in date_diffs)),
    # "is_bimonthly_emmanuel2": int(any(55 <= d <= 65 for d in date_diffs)),
    # "is_quarterly_emmanuel2": int(any(85 <= d <= 95 for d in date_diffs)),
    # "is_annual_emmanuel2": int(any(360 <= d <= 370 for d in date_diffs)),
    # }

    return {
        # **recurrence_flags,
        # "avg_days_between_emmanuel2": avg_days_between,
        # "std_days_between_emmanuel2": std_days_between,
        "recurrence_score_emmanuel2": recurrence_score,
    }


def get_recurring_consistency_score(transaction: Transaction, transactions: list[Transaction]) -> dict:
    """Computes a consistency score to minimize bias errors in recurring transaction detection."""

    merchant_txns = [t for t in transactions if t.name == transaction.name]

    if len(merchant_txns) < 2:
        return {"recurring_consistency_score_emmanuel2": 0.0}  # Not enough data to determine recurrence

    dates = sorted(datetime.strptime(t.date, "%Y-%m-%d") for t in merchant_txns)
    date_diffs = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]

    avg_days_between = mean(date_diffs)
    std_days_between = stdev(date_diffs) if len(date_diffs) > 1 else 0.0

    amount_variations = [t.amount for t in merchant_txns]
    amount_stability = 1 - (stdev(amount_variations) / (mean(amount_variations) + 1e-6))  # Normalize stability score

    # Frequency-based confidence (e.g., monthly = strong, yearly = weaker)
    recurrence_flags = {
        "biweekly_emmanuel2": int(14 in date_diffs),
        "monthly_emmanuel2": int(any(27 <= d <= 31 for d in date_diffs)),
        "bimonthly_emmanuel2": int(any(55 <= d <= 65 for d in date_diffs)),
        "quarterly_emmanuel2": int(any(85 <= d <= 95 for d in date_diffs)),
        "annual_emmanuel2": int(any(360 <= d <= 370 for d in date_diffs)),
    }

    # Weight factors based on common recurrence patterns
    recurrence_weight = (
        0.4 * recurrence_flags["monthly_emmanuel2"]
        + 0.2 * recurrence_flags["biweekly_emmanuel2"]
        + 0.15 * recurrence_flags["bimonthly_emmanuel2"]
        + 0.1 * recurrence_flags["quarterly_emmanuel2"]
        + 0.05 * recurrence_flags["annual_emmanuel2"]
    )

    # Final consistency score (scales from 0 to 1)
    consistency_score = (
        0.5 * amount_stability  # Amount consistency
        + 0.3 * (1 - (std_days_between / (avg_days_between + 1e-6)))  # Time interval consistency
        + 0.2 * recurrence_weight  # Frequency confidence
    )

    return {"recurring_consistency_score_emmanuel2": round(max(0, min(consistency_score, 1)), 2)}


def validate_recurring_transaction(transaction: Transaction, threshold: int = 80) -> bool:
    """Determines if a transaction should be classified as recurring based on vendor trends."""
    vendor_name = transaction.name.lower()

    # Fuzzy Matching for Vendor Detection
    match_result: tuple[str, int] | None = process.extractOne(vendor_name, RECURRING_VENDORS)

    # If no match is found, return False
    if match_result is None:
        return False

    # Extract the best match and its score
    best_match, score = match_result

    # Return True if the score is above the threshold
    return score > threshold


def classify_subscription_tier(transaction: Transaction) -> int:
    """Dynamically classifies a transaction's subscription tier."""
    subscription_tiers = {
        "netflix": [(8.99, 1), (15.49, 2), (19.99, 3)],
        "spotify": [(9.99, 1), (12.99, 2), (15.99, 3)],
        "disney+": [(7.99, 1), (13.99, 2)],
    }

    vendor_name = transaction.name.lower()
    amount = transaction.amount

    return next((tier for price, tier in subscription_tiers.get(vendor_name, []) if price == amount), 0)


def get_amount_features(transaction: Transaction, transactions: list[Transaction]) -> dict:
    """Extracts features related to amount stability using clustering."""
    vendor_txns = [t.amount for t in transactions if t.name == transaction.name]

    if not vendor_txns:
        return {"is_fixed_amount_recurring": 0, "amount_fluctuation": 0.0, "price_cluster": -1}

    price_fluctuation = max(vendor_txns) - min(vendor_txns)

    # Handle edge cases for KMeans clustering
    if len(vendor_txns) < 3 or len(set(vendor_txns)) == 1:
        return {
            # "is_fixed_amount_recurring_emmanuel2": int(max(vendor_txns) <= min(vendor_txns) * 1.02),
            "amount_fluctuation_emmanuel2": price_fluctuation,
            # "price_cluster_emmanuel2": -1,  # Indicates clustering was not performed
        }

    # Perform KMeans clustering
    # amounts = np.array(vendor_txns).reshape(-1, 1)
    # kmeans = KMeans(n_clusters=min(3, len(set(vendor_txns))), random_state=42).fit(amounts)
    # price_cluster = kmeans.predict([[transaction.amount]])[0]

    return {
        # "is_fixed_amount_recurring_emmanuel2": int(max(vendor_txns) <= min(vendor_txns) * 1.02),
        "amount_fluctuation_emmanuel2": price_fluctuation,
        # "price_cluster_emmanuel2": price_cluster,
    }


def get_user_behavior_features(transaction: Transaction, transactions: list[Transaction]) -> dict:
    """Extracts user-level spending behavior."""
    user_txns = [t.amount for t in transactions if t.user_id == transaction.user_id]

    if not user_txns:
        return {
            # "user_avg_spent_emmanuel2": 0.0,
            "user_total_spent_emmanuel2": 0.0,
            # "user_subscription_count_emmanuel2": 0,
        }

    # Ensure subscriptions are only counted for the given user
    # user_subscription_count = sum(t.name in RECURRING_VENDORS for t in transactions
    #                               if t.user_id == transaction.user_id)

    return {
        # "user_avg_spent_emmanuel2": mean(user_txns),
        "user_total_spent_emmanuel2": sum(user_txns),
        # "user_subscription_count_emmanuel2": user_subscription_count,
    }


def get_refund_features(transaction: Transaction, transactions: list[Transaction]) -> dict:
    """Extracts refund-related features."""
    refunds = [t for t in transactions if t.amount == -transaction.amount]

    if not refunds:
        return {
            # "refund_rate_emmanuel2": 0.0,
            "avg_refund_time_lag_emmanuel2": 0.0,
        }

    refund_time_lags = [
        (datetime.strptime(t.date, "%Y-%m-%d") - datetime.strptime(transaction.date, "%Y-%m-%d")).days for t in refunds
    ]

    return {
        # "refund_rate_emmanuel2": len(refunds) / len(transactions),
        "avg_refund_time_lag_emmanuel2": mean(refund_time_lags) if refund_time_lags else 0.0,
    }


def get_monthly_spending_trend(transaction: Transaction, transactions: list[Transaction]) -> dict:
    """Calculates the total spending for the transaction's month."""
    month_year = transaction.date[:7]  # Extracts YYYY-MM
    monthly_spending = sum(t.amount for t in transactions if t.date.startswith(month_year))

    return {"monthly_spending_trend_emmanuel2": monthly_spending}
