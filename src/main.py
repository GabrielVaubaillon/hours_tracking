#!/bin/python
""" """

import argparse
import datetime
import logging
import re
from pathlib import Path


def parse_dates(str_: str) -> dict[str, str]:

    # TODO: no errors by lines here?
    pattern = re.compile(
        r"^(\d{4}-\d{2}-\d{2}) (.*?)$",  # TODO
        re.MULTILINE,
    )
    dates = {date_str: description for date_str, description in re.findall(pattern, str_)}
    return dates


def load_date_file(input_file: Path) -> dict[str, str]:
    assert input_file.is_file()

    with open(input_file, mode="rt", encoding="utf_8", errors="strict") as fh:
        str_ = fh.read()

    return parse_dates(str_)


def parse_cli_args():
    parser = argparse.ArgumentParser()
    # parser.add_argument()
    return parser.parse_args()


def main():
    pass


def test():
    # Date parsing
    str_date: str = (
        "2025-04-12 test 1\n" "2025-04-14 test 2\n" "2024-12-24 test 3\n" "24-1-24 test missing\n"
    )
    expected_dates = {"2025-04-12": "test 1", "2025-04-14": "test 2", "2024-12-24": "test 3"}
    dates: dict[str, str] = parse_dates(str_date)
    assert dates == expected_dates


if __name__ == "__main__":
    test()
    main()
