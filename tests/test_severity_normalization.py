from core.cli import _norm_severity


def test_norm_severity_variants():
    cases = {
        None: "Unknown",
        "": "Unknown",
        "P0": "P0",
        "p1": "P1",
        "High": "High",
        "medium": "Medium",
        "LOW": "Low",
        "weird": "Unknown",
    }
    for raw, expected in cases.items():
        assert _norm_severity(raw) == expected
