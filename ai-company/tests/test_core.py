import json
import unittest
from dataclasses import FrozenInstanceError
from datetime import date

from core import (DEPARTMENTS, BROADCAST, Company, DepartmentAgent, EventLog, Kpi, Message, MessageBus,
                  MockLLM, Role, SimClock, Task, class_name_for, publishes_for, subscribes_for,
                  validate_topic_map)
from core.llm import LLMProvider


class Recorder(DepartmentAgent):
    """Test agent: records deliveries, optionally replies."""

    def __init__(self, *a, subs=(), reply_topic=None, **k):
        super().__init__(*a, **k)
        self.SUBSCRIBES = tuple(subs)
        self.received = []
        self.reply_topic = reply_topic

    def handle(self, message):
        self.received.append(message)
        if self.reply_topic:
            return [self.reply(message, self.reply_topic, {"ok": True})]
        return []


def make(name, subs=(), reply_topic=None, bus=None, clock=None, log=None):
    clock = clock if clock is not None else SimClock()
    bus = bus if bus is not None else MessageBus(clock)
    log = log if log is not None else EventLog(clock.start)
    role = Role("Head", name, "head")
    return Recorder(name, name, role, MockLLM(), bus, clock, log, subs=subs, reply_topic=reply_topic)


class SchemaTests(unittest.TestCase):
    def test_frozen_and_validation(self):
        m = Message("1", "a", "b", "sales.deal_won", {"x": 1}, 0)
        with self.assertRaises(FrozenInstanceError):
            m.topic = "x.y"
        with self.assertRaises(ValueError):
            Message("1", "a", "b", "BadTopic", {}, 0)
        with self.assertRaises(ValueError):
            Task("t", "title", "o", status="weird")
        with self.assertRaises(ValueError):
            Role("r", "sales", "manager", salary_band_gbp=(10, 5))

    def test_kpi_attainment(self):
        self.assertAlmostEqual(Kpi("rev", "GBP", 100, 80).attainment, 0.8)
        self.assertTrue(Kpi("dso", "days", 45, 40, higher_is_better=False).on_track)
        self.assertIsNone(Kpi("x", "n", 1).attainment)


class ClockTests(unittest.TestCase):
    def test_advance(self):
        c = SimClock()
        self.assertEqual((c.day, c.tick, c.date), (0, 0, date(2026, 1, 5)))
        c.advance(3)
        c.advance_days(4)
        self.assertEqual((c.day, c.date), (7, date(2026, 1, 12)))
        self.assertEqual(c.year_index, 1)
        self.assertTrue(c.every(7))
        with self.assertRaises(ValueError):
            c.advance(-1)

    def test_days_per_tick(self):
        c = SimClock(days_per_tick=7)
        c.advance(2)
        self.assertEqual((c.day, c.tick), (14, 2))


class BusTests(unittest.TestCase):
    def test_broadcast_order_and_exclusion(self):
        clock = SimClock()
        bus = MessageBus(clock)
        agents = {n: make(n, subs=["sales.*"], bus=bus, clock=clock) for n in ("zeta", "alpha", "mid")}
        order = []
        for a in agents.values():
            bus.register(a)
            orig = a.handle
            a.handle = lambda m, orig=orig, n=a.name: (order.append(n), orig(m))[1]
        sender = make("sales", bus=bus, clock=clock)
        bus.register(sender)
        for i in range(2):
            bus.publish(bus.make_message("sales", BROADCAST, "sales.deal_won", {"i": i}))
        bus.step()
        self.assertEqual(order, ["alpha", "mid", "zeta", "alpha", "mid", "zeta"])
        self.assertEqual([m.body["i"] for m in agents["alpha"].received], [0, 1])
        self.assertEqual(sender.received, [])

    def test_direct_dead_letter_and_dedupe(self):
        clock = SimClock()
        bus = MessageBus(clock)
        a = make("a", bus=bus, clock=clock)
        bus.register(a)
        m = bus.make_message("x", "a", "x.ping")
        self.assertTrue(bus.publish(m))
        self.assertFalse(bus.publish(m))
        bus.publish(bus.make_message("x", "nobody", "x.ping"))
        bus.step()
        self.assertEqual(len(a.received), 1)
        self.assertEqual(len(bus.dead_letters), 1)

    def test_replies_delivered_next_step_and_future_messages_wait(self):
        clock = SimClock()
        bus = MessageBus(clock)
        a = make("a", subs=["b.pong"], bus=bus, clock=clock)
        b = make("b", subs=["a.ping"], reply_topic="b.pong", bus=bus, clock=clock)
        a.PUBLISHES = ()
        bus.register(a)
        bus.register(b)
        a.emit("a.ping", {}, recipient="b")
        a.emit("a.ping", {}, recipient="b", delay_days=2)
        self.assertEqual(len(bus.step()), 1)      # only the due one
        self.assertEqual(len(b.received), 1)
        self.assertEqual(len(bus.step()), 1)      # the reply
        self.assertEqual(a.received[0].reply_to, b.received[0].id)
        clock.advance(2)
        bus.drain()
        self.assertEqual(len(b.received), 2)

    def test_emit_enforces_prefix_and_publishes(self):
        a = make("sales")
        with self.assertRaises(ValueError):
            a.emit("finance.invoice_issued")
        a.PUBLISHES = ("sales.deal_won",)
        a.emit("sales.deal_won")
        a.emit("sales.internal.note")
        with self.assertRaises(ValueError):
            a.emit("sales.deal_lost")


class EventLogTests(unittest.TestCase):
    def test_query_and_jsonl(self):
        log = EventLog(date(2026, 1, 5))
        log.append(0, "sales", "sales.deal_won", "won", {"deal_id": "DL-1"})
        log.append(1, "finance", "finance.invoice_issued", "inv")
        log.append(5, "sales", "sales.deal_lost")
        self.assertEqual(len(log.query(department="sales")), 2)
        self.assertEqual(len(log.query(topic="sales.*")), 2)
        self.assertEqual(len(log.query(topic="sales.deal_won")), 1)
        self.assertEqual(len(log.query(since=1, until=4)), 1)
        lines = log.to_jsonl().splitlines()
        self.assertEqual(len(lines), 3)
        first = json.loads(lines[0])
        self.assertEqual((first["seq"], first["date"], first["data"]), (0, "2026-01-05", {"deal_id": "DL-1"}))
        self.assertEqual(log.to_jsonl(), log.to_jsonl())


class MockLLMTests(unittest.TestCase):
    def test_scripted_and_default(self):
        llm = MockLLM({"invoice": "INV!", "deal": lambda s, p: "DEAL:" + p[:4]})
        self.assertIsInstance(llm, LLMProvider)
        self.assertEqual(llm.complete("sys", "Draft an INVOICE"), "INV!")
        self.assertEqual(llm.complete("sys", "deal terms"), "DEAL:deal")
        self.assertEqual(llm.complete("s", "unknown   thing"), "[mock] unknown thing")
        self.assertEqual(llm.complete("s", "unknown   thing"), llm.complete("s", "unknown   thing"))
        self.assertEqual(len(llm.calls), 5)


class TopicMapTests(unittest.TestCase):
    def test_map_is_consistent(self):
        self.assertEqual(validate_topic_map(), [])
        self.assertEqual(len(DEPARTMENTS), 12)

    def test_lifecycle_topics_present(self):
        chain = ["marketing.lead_generated", "sales.lead_qualified", "sales.proposal_sent", "sales.deal_won",
                 "legal.contract_signed", "delivery.engagement_kickoff", "finance.invoice_issued",
                 "finance.payment_received", "finance.invoice_overdue", "customer_success.renewal_due",
                 "customer_success.renewal_confirmed"]
        for t in chain:
            self.assertIn(t, publishes_for(t.split(".")[0]))

    def test_class_names(self):
        self.assertEqual(class_name_for("it_security"), "ItSecurityAgent")
        self.assertEqual(class_name_for("customer_success"), "CustomerSuccessAgent")
        self.assertIn("sales.deal_won", subscribes_for("finance"))


class CompanyTests(unittest.TestCase):
    def test_registers_twelve_stubs_and_runs(self):
        company = Company(use_departments=False)
        self.assertEqual(tuple(company.agents), DEPARTMENTS)
        self.assertEqual(company.bus.agent_names, sorted(DEPARTMENTS))
        company.inject("marketing.lead_generated", {"lead_id": "LD-00001"})
        company.inject("marketing.lead_generated", {"lead_id": "LD-00002"}, delay_days=3)
        log = company.run(5)
        self.assertEqual(company.clock.day, 5)
        got = log.query(topic="stub.received")
        self.assertEqual(sorted({e.department for e in got}), ["data", "sales"])
        self.assertEqual(len(got), 4)
        self.assertEqual(len(log.query(topic="system.tick")), 5)

    def test_custom_factory_chain_is_deterministic(self):
        def run_once():
            def f_sales(llm, bus, clock, log):
                a = make("sales", subs=["marketing.lead_generated"], reply_topic="sales.lead_qualified",
                         bus=bus, clock=clock, log=log)
                return a
            company = Company(factories={"sales": f_sales})
            company.inject("marketing.lead_generated", {"lead_id": "LD-1"})
            return company.run(2).to_jsonl()
        out = run_once()
        self.assertEqual(out, run_once())
        self.assertIn("sales.lead_qualified", out)

    def test_nonstrict_logs_agent_errors(self):
        class Boom(DepartmentAgent):
            SUBSCRIBES = ("marketing.lead_generated",)

            def handle(self, message):
                raise RuntimeError("boom")

        company = Company(use_departments=False, strict=False, factories={
            "sales": lambda llm, bus, clock, log: Boom("sales", "sales", Role("Head", "sales", "head"),
                                                      llm, bus, clock, log)})
        company.inject("marketing.lead_generated", {})
        log = company.run(1)
        self.assertEqual(len(log.query(topic="system.agent_error")), 1)
        with self.assertRaises(ValueError):
            Company(factories={"nope": None})


if __name__ == "__main__":
    unittest.main()
