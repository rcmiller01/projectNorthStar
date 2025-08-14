from ingest import parse_log
from pathlib import Path


def test_parse_log_samples():
    p = Path('samples/app.log')
    assert p.exists(), 'samples/app.log missing'
    recs = parse_log(str(p))
    assert recs, 'no records parsed'
    # ensure some metadata present
    has_ts = any(r['meta'].get('timestamp') for r in recs)
    has_comp = any(r['meta'].get('component') for r in recs)
    assert has_ts and has_comp
