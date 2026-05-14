from rootcause.runner import FailureReport, parse_failure

def test_parse_failure_pytest():
    report = FailureReport(
        command="pytest tests/test_auth.py",
        exit_code=1,
        stdout="""
___________________________________ test_login ___________________________________

    def test_login():
>       assert login('user', 'pass') == True
E       AssertionError: assert False == True

tests/test_auth.py:15: AssertionError
        """,
        stderr="",
        runtime_seconds=0.1,
        framework="pytest"
    )

    parse_failure(report)

    assert report.test_name == "test_login"
    assert report.error_type == "AssertionError"
    assert len(report.locations) > 0
    assert report.locations[0]["file"] == "tests/test_auth.py"
    assert report.locations[0]["line"] == 15
