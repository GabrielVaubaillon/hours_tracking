#!/bin/python
""" """

VERSION = "dev"

import argparse
import datetime
import logging
import re
from dataclasses import dataclass
from pathlib import Path

WEEKDAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
WEEKDAYS_FULL = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
MONTHS = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")
MONTHS_FULL = (
    "january",
    "febuary",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
)


@dataclass
class Configuration:
    day_worked: tuple[str, ...] = ("mon", "tue", "wed", "thu", "fri")
    pass


class Date(datetime.date):
    def __init__(self, *args, description: str = "", **kwargs):
        super().__init__()

        self.description = description

    def add_description(self, description: str):
        self.description = description
        return self

    def str_weekday(self):
        return WEEKDAYS[self.weekday()]


def parse_dates(str_: str, quiet: bool = False) -> list[Date]:

    # TODO: no errors by lines here?
    pattern = re.compile(
        r"^(\d{4}-\d{2}-\d{2}) (.*?)$",  # TODO
        re.MULTILINE,
    )
    dates: list[Date] = []
    # errors = {}
    for date_str, description in re.findall(pattern, str_):
        try:
            date = Date.fromisoformat(date_str)
        except ValueError as error:
            if not quiet:
                print(f"WARNING: {date_str} - {error}")
            # errors[date_str] = error.__str__()
            continue
        date.add_description(description)
        dates.append(date)
    return dates


def load_date_file(input_file: Path) -> list[Date]:
    assert input_file.is_file()

    with open(input_file, mode="rt", encoding="utf_8", errors="strict") as fh:
        str_ = fh.read()

    return parse_dates(str_)


def report(
    start_date: Date,
    end_date: Date,
    holidays: list[Date] | None = None,
    quiet: bool = False,
) -> dict[str, int]:

    delta: datetime.timedelta = (end_date - start_date) + datetime.timedelta(days=1)
    total_days: int = delta.days
    complete_weeks: int = total_days // 7

    if holidays is None:
        holidays = []
    # TODO: if this part gets to long, use better search algorithms
    holidays_in_range: list[Date] = [
        date for date in holidays if date >= start_date and date <= end_date
    ]

    date_range: list[Date] = [start_date + datetime.timedelta(days=i) for i in range(total_days)]

    working_days: int = 0
    off_days: int = 0
    holidays_on_working_day: int = 0
    for date in date_range:
        if date in holidays_in_range:
            off_days += 1
            if date.str_weekday() in config.day_worked:
                holidays_on_working_day += 1
        elif date.str_weekday() in config.day_worked:
            working_days += 1
        else:
            off_days += 1

    if not quiet:
        print(
            f"Report between {start_date.strftime("%A %Y-%m-%d")}"
            f" and {end_date.strftime("%A %Y-%m-%d")}\n"
            f" - total days: {total_days}  ({total_days / 7:.1f} weeks)\n"
            f" - working days: {working_days}\n"
            f" - off days: {off_days}"
            f" (including {len(holidays_in_range)} holidays)\n"
        )
    results = {
        "total_days": total_days,
        "working_days": working_days,
        "off_days": off_days,
        "relevant_holidays": holidays_on_working_day,
        "total_holidays": len(holidays_in_range),
    }
    return results


def date_iso_or_today(date_str):
    if date_str == "today":
        return Date.today()
    return Date.fromisoformat(date_str)


def parse_cli_args(args: list[str] | None = None):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--report",
        action="store",
        nargs=2,
        required=False,
        type=date_iso_or_today,
        help="Produce a basic report of the period between two dates",
    )

    parser.add_argument("--verbose", "-v", action="count", default=0)
    parser.add_argument("--quiet", "-q", action="store_true")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")

    return parser.parse_args() if args is None else parser.parse_args(args)


def main():
    global config

    config = Configuration()
    cli_args = parse_cli_args()
    test()

    if cli_args.report:
        report(
            start_date=min(cli_args.report),
            end_date=max(cli_args.report),
        )


def test() -> int:
    global config
    config = Configuration()

    # Date parsing
    # ------------
    str_date: str = (
        "2025-04-12 test 1\n"
        "2025-04-14 test 2\n"
        "2024-12-24 test 3\n"
        "24-1-24 test missing\n"
        "2025-06-19 test 4\n"
        "2025-65-14 invalid month\n"
        "2024-12-32 invalid day\n"
    )
    expected_dates = [
        Date(2025, 4, 12).add_description("test 1"),
        Date(2025, 4, 14).add_description("test 2"),
        Date(2024, 12, 24).add_description("test 3"),
        Date(2025, 6, 19).add_description("test 4"),
    ]
    dates: list[Date] = parse_dates(str_date, quiet=True)
    assert dates == expected_dates, f"parse_date() return invalid object\n{dates}\n{expected_dates}"

    bank_holidays: list[Date] = parse_dates(
        # 2024
        "2024-01-01 New Year's Day\n"
        "2024-02-05 St Brigid's Day\n"
        "2024-03-18 Saint Patrick's Day\n"
        "2024-04-01 Easter Monday\n"
        "2024-05-06 May Day\n"
        "2024-06-03 June Bank Holiday\n"
        "2024-08-05 August Bank Holiday\n"
        "2024-10-28 October Bank Holiday\n"
        "2024-12-25 Christmas Day\n"
        "2024-12-26 St Stephens's Day\n"
        # 2025
        "2025-01-01 New Year's Day\n"
        "2025-02-03 St Brigid's Day\n"
        "2025-03-17 Saint Patrick's Day\n"
        "2025-04-21 Easter Monday\n"
        "2025-05-05 May Day\n"
        "2025-06-02 June Bank Holiday\n"
        "2025-08-04 August Bank Holiday\n"
        "2025-10-27 October Bank Holiday\n"
        "2025-12-25 Christmas Day\n"
        "2025-12-26 St Stephens's Day\n"
        # 2026
        "2026-01-01 New Year's Day\n"
        "2026-02-02 St Brigid's Day\n"
        "2026-03-17 Saint Patrick's Day\n"
        "2026-04-06 Easter Monday\n"
        "2026-05-04 May Day\n"
        "2026-06-01 June Bank Holiday\n"
        "2026-08-03 August Bank Holiday\n"
        "2026-10-26 October Bank Holiday\n"
        "2026-12-25 Christmas Day\n"
        "2026-12-26 St Stephens's Day\n"
    )

    # Report generation
    # -----------------
    results: dict[str, int]
    results = report(
        start_date=Date(2025, 4, 4),
        end_date=Date(2025, 4, 23),
        holidays=bank_holidays,
        quiet=True,
    )
    expected_results = {
        "total_days": 20,
        "working_days": 13,
        "off_days": 7,
        "relevant_holidays": 1,
        "total_holidays": 1,
    }
    assert (
        results == expected_results
    ), f"report() return invalid values\n{results}\n{expected_results}"

    results = report(
        start_date=Date(2025, 4, 7),
        end_date=Date(2025, 4, 20),
        holidays=bank_holidays,
        quiet=True,
    )
    expected_results = {
        "total_days": 14,
        "working_days": 10,
        "off_days": 4,
        "relevant_holidays": 0,
        "total_holidays": 0,
    }
    assert (
        results == expected_results
    ), f"report() return invalid values\n{results}\n{expected_results}"

    results = report(
        start_date=Date(2025, 4, 4),
        end_date=Date(2026, 4, 23),
        holidays=bank_holidays,
        quiet=True,
    )
    expected_results = {
        "total_days": 385,
        "working_days": 264,
        "off_days": 121,
        "relevant_holidays": 11,
        "total_holidays": 11,
    }
    assert (
        results == expected_results
    ), f"report() return invalid values\n{results}\n{expected_results}"

    return 0


if __name__ == "__main__":
    main()
