from unifs.tui import format_table


def test_format_table():
    output = format_table(
        header=["FOO", "BAR", "BAZZZ"],
        widths=[10, 5, 5],
        rows=[
            ("Hello", 42, None),
            ("What a wonderful world", 75014, False),
        ],
    )
    assert (
        output
        == """
FOO       BAR  B...
Hello     42
What a... 7... F...
""".strip()
    )
