from app import parse_line_statuses


def test_parse_line_statuses():
    fake_data = [
        {"name": "Central", "lineStatuses": [{"statusSeverityDescription": "Good Service"}]}
    ]

    result = parse_line_statuses(fake_data)

    assert result == [{"line": "Central", "status": "Good Service"}]
