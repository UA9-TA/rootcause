def test_pytest_plugin_tracing():
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/fixtures/sample_failing_test.py"],
        env={"PYTEST_PLUGINS": "rootcause.pytest_plugin"},
        capture_output=True,
        text=True
    )
    # the plugin should have successfully injected and run
    assert "test_token_expiration" in result.stdout
