#!/bin/python
""" """

VERSION = "dev"

import argparse
import datetime
import logging
import re
from dataclasses import dataclass
from pathlib import Path

# TODO: WTH are you trying to do?
weekdays = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


@dataclass
class Configuration:
    day_worked: tuple[str, ...] = ("mon", "tue", "wed", "thu", "fri")
    pass


class Date(datetime.date):
    def __init__(self, description: str = "", **kwargs):
        super().__init__(**kwargs)

        self.description = description


def parse_dates(str_: str) -> dict[datetime.date, str]:

    # TODO: no errors by lines here?
    pattern = re.compile(
        r"^(\d{4}-\d{2}-\d{2}) (.*?)$",  # TODO
        re.MULTILINE,
    )
    dates = {}
    # errors = {}
    for date_str, description in re.findall(pattern, str_):
        try:
            date = datetime.date.fromisoformat(date_str)
        except ValueError as error:
            print(f"WARNING: {date_str} - {error}")
            # errors[date_str] = error.__str__()
            continue
        dates[date] = description
    return dates


def load_date_file(input_file: Path) -> dict[datetime.date, str]:
    assert input_file.is_file()

    with open(input_file, mode="rt", encoding="utf_8", errors="strict") as fh:
        str_ = fh.read()

    return parse_dates(str_)


def parse_cli_args(args: list[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="count", default=0)
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("--quiet", "-q", action="store_true")
    if args is None:
        cli_args = parser.parse_args()
    else:
        cli_args = parser.parse_args(args)
    return cli_args


def main():

    cli_args = parse_cli_args()

    test()
    pass


def test():
    # Date parsing
    str_date: str = (
        "2025-04-12 test 1\n"
        "2025-04-14 test 2\n"
        "2024-12-24 test 3\n"
        "24-1-24 test missing\n"
        "2025-06-19 test 4\n"
        "2025-65-14 invalid month\n"
        "2024-12-32 invalid day\n"
    )
    expected_dates = {
        datetime.date(2025, 4, 12): "test 1",
        datetime.date(2025, 4, 14): "test 2",
        datetime.date(2024, 12, 24): "test 3",
        datetime.date(2025, 6, 19): "test 4",
    }
    dates: dict[datetime.date, str] = parse_dates(str_date)
    assert dates == expected_dates

    cli_args = parse_cli_args(["--verbose"])
    assert isinstance(cli_args.quiet, bool) and not cli_args.quiet
    assert isinstance(cli_args.verbose, int) and cli_args.verbose == 1

    cli_args = parse_cli_args(["-vvv"])
    assert isinstance(cli_args.quiet, bool) and not cli_args.quiet
    assert isinstance(cli_args.verbose, int) and cli_args.verbose == 3

    cli_args = parse_cli_args(["--quiet"])
    assert isinstance(cli_args.quiet, bool) and cli_args.quiet
    assert isinstance(cli_args.verbose, int) and cli_args.verbose == 0


if __name__ == "__main__":
    main()
