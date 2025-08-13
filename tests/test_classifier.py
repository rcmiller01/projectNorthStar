from pipeline.classifier import classify, ClassificationResult


def test_empty() -> None:
    res = classify("")
    assert isinstance(res, ClassificationResult)
    assert res.category == "unknown"
    assert res.confidence == 0.0


def test_billing_keyword() -> None:
    res = classify("I have a billing question about my invoice")
    assert res.category == "billing"
    assert res.confidence >= 0.6
