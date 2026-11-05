"""python3 -m core [days] [--jsonl PATH]  (run from the ai-company directory)."""

import sys

from . import Company


def main(argv: list[str]) -> None:
    days = int(argv[0]) if argv and argv[0].isdigit() else 30
    company = Company(strict=False)
    log = company.run(days)
    print(f"Ran {days} days, {len(log)} events, {len(company.bus.history)} messages delivered")
    for dept, n in log.count_by("department").items():
        print(f"  {dept:18s} {n}")
    if "--jsonl" in argv:
        log.write_jsonl(argv[argv.index("--jsonl") + 1])


if __name__ == "__main__":
    main(sys.argv[1:])
