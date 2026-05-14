from rootcause.analyzer import Analysis

def test_analysis_dataclass():
    analysis = Analysis(
        root_cause="Test root cause",
        location="file.py:1",
        explanation="Explanation text",
        fix="Fix code",
        also_found=["Other issue"],
        confidence=95,
        fix_diff="diff code"
    )

    assert analysis.root_cause == "Test root cause"
    assert analysis.confidence == 95
    assert len(analysis.also_found) == 1
