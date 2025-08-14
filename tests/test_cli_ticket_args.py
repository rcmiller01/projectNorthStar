from core.cli import build_parser


def test_cli_mutual_exclusion():
    p = build_parser()
    # title variant
    args = p.parse_args(["triage", "--title", "A", "--body", "B"])
    assert getattr(args, "ticket_id", None) is None
    # ticket id variant
    args2 = p.parse_args(["triage", "--ticket-id", "T-1"])
    assert args2.ticket_id == "T-1"
    assert getattr(args2, "title", None) is None


def test_cli_defaults_ticket():
    p = build_parser()
    args = p.parse_args(["triage", "--ticket-id", "T-2"])
    assert args.max_comments == 5
    assert args.no_write is False
