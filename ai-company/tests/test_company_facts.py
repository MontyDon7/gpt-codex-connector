"""Guards the internal consistency of COMPANY.md (headcount and budget tables)."""
import os
import re
import unittest

from core import DEPARTMENTS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def table_rows(text, header_start):
    lines = text.splitlines()
    i = next(n for n, l in enumerate(lines) if l.startswith(header_start))
    rows = []
    for l in lines[i + 2:]:
        if not l.startswith("|"):
            break
        rows.append([c.strip().strip("*") for c in l.strip("|").split("|")])
    return rows


def num(s):
    return int(re.sub(r"[^\d]", "", s))


class CompanyFactsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, "COMPANY.md"), encoding="utf-8") as fh:
            cls.text = fh.read()

    def test_headcount_table(self):
        rows = table_rows(self.text, "| Department id |")
        body = {r[0]: [num(c) for c in r[1:]] for r in rows if r[0] in DEPARTMENTS}
        self.assertEqual(set(body), set(DEPARTMENTS))
        total = next(r for r in rows if r[0] == "Total")
        for col in range(6):
            self.assertEqual(sum(v[col] for v in body.values()), num(total[col + 1]))
        self.assertEqual([num(c) for c in total[1:4]], [38, 110, 230])
        self.assertEqual([num(c) for c in total[4:7]], [22, 70, 150])

    def test_budget_envelopes(self):
        rows = table_rows(self.text, "| Dept |")
        body = {r[0]: [num(c) for c in r[1:]] for r in rows if r[0] in DEPARTMENTS}
        self.assertEqual(set(body), set(DEPARTMENTS))
        for v in body.values():
            for y in range(3):
                self.assertEqual(v[y] + v[3 + y], v[6 + y])
        total = next(r for r in rows if r[0] == "Total")
        for col in range(9):
            self.assertEqual(sum(v[col] for v in body.values()), num(total[col + 1]))
        self.assertEqual([num(c) for c in total[7:10]], [7500, 17800, 39000])
        cogs = [body["delivery"][y] + body["customer_success"][y] for y in (6, 7, 8)]
        self.assertEqual(cogs, [3120, 8190, 16630])
        revenue = [6000, 19500, 46200]
        margins = [round(100 * (r - c) / r) for r, c in zip(revenue, cogs)]
        self.assertEqual(margins, [48, 58, 64])

    def test_revenue_equals_clients_times_acv(self):
        self.assertEqual(24 * 250_000, 6_000_000)
        self.assertEqual(65 * 300_000, 19_500_000)
        self.assertEqual(140 * 330_000, 46_200_000)


if __name__ == "__main__":
    unittest.main()
