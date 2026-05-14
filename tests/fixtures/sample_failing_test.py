import datetime

def is_token_expired(exp_time: datetime.datetime) -> bool:
    """Check if a JWT expiration time has passed."""
    # Bug: using datetime.now() (local time) compared to likely UTC exp_time
    now = datetime.datetime.now()
    return now > exp_time

def test_token_expiration():
    # Simulate a token that expires 5 minutes from now in UTC
    exp_time = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(minutes=5)

    # In systems behind UTC (e.g. PST), local time could be hours behind, so this would be False
    # BUT if system is ahead of UTC (e.g. IST), local time is hours ahead, so this would be True incorrectly
    # We will simulate a failure by using a fake time

    # Just force a simple assertion failure for the demo fixture that mimics the README
    fake_local_time = exp_time + datetime.timedelta(hours=2) # e.g. UTC+2 timezone

    assert fake_local_time <= exp_time, "JWT token comparison fails on non-UTC systems"
