"""IT and Security scenarios (Lumenhall Partners).

Each ``scenario_*`` function only builds Messages with ``bus.make_message``; the caller seeds them with
``Company.seed``. Chains follow CONVENTIONS.md 7.2 (hiring, security incident, vendors, compliance); the SLA values
follow sops.md. Clients are fictional (COMPANY.md section 10); amounts are modelled GBP.
"""

from __future__ import annotations

from core import Message, MessageBus, SimClock


def scenario_phishing_to_breach(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A critical credential-phishing alert exposes client personal data (SOP-IT_SECURITY-01 and -02).

    Expected chain: external.security_alert -> it_security.incident_detected (executive, legal, operations,
    customer_success, delivery) -> it_security.data_breach_confirmed (legal, executive, customer_success);
    legal.regulator_notification_filed (inside 72 hours) -> it_security.incident_resolved.
    """
    d = clock.day
    cid = params.get("client_id", "CL-0007")
    alert = {
        "summary": "Delivery consultant mailbox compromised via credential phishing; forwarding rule exfiltrates "
                   "client engagement files", "severity": "critical", "client_id": cid,
        "client_name": params.get("client_name", "Calder Freight Group"), "asset": "mailbox:delivery-consultant-07",
        "indicator": "inbox-rule-forward-external", "source": "google_workspace_alert_centre",
        "category": "phishing", "personal_data_involved": True, "data_subjects_estimate": 180,
        "data_categories": ["client_employee_contact_data", "shift_rota_extracts"], "unauthorised_access": True,
    }
    filed = {"summary": "ICO notification filed under UK GDPR Article 33", "client_id": cid,
             "filing_reference": params.get("filing_reference", "ICO-2026-CALDER-001"), "severity": "critical"}
    return [
        bus.make_message("external", "it_security", "external.security_alert", alert, sim_time=d),
        bus.make_message("legal", "it_security", "legal.regulator_notification_filed", filed,
                         sim_time=d + params.get("filing_delay_days", 2)),
    ]


def scenario_joiner_mover_leaver(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A cohort of joiners, a contractor and two leavers (SOP-IT_SECURITY-04 and -05).

    Expected chain: people.new_hire_started -> it_security.access_provisioned (people, operations);
    people.contractor_engaged -> access_provisioned with an expiry; people.employee_left (one involuntary, one
    privileged) -> it_security.access_revoked (people, legal), with an incident for suspected exfiltration.
    """
    d = clock.day
    return [
        bus.make_message("people", "it_security", "people.new_hire_started", {
            "employee_id": "EMP-0031", "role": "Consultant", "department": "delivery", "start_day": d + 3,
            "manager": "EMP-0009", "client_workspaces": ["Calder Freight Group"], "confidentiality_agreement": True,
            "summary": "Consultant joins the Calder Freight engagement team"}, sim_time=d),
        bus.make_message("people", "it_security", "people.new_hire_started", {
            "employee_id": "EMP-0032", "role": "Billing and Collections Specialist", "department": "finance",
            "start_day": d + 5, "manager": "EMP-0004", "summary": "Finance specialist joins"}, sim_time=d),
        bus.make_message("people", "it_security", "people.new_hire_started", {
            "employee_id": "EMP-0033", "role": "Security and IT Operations Specialist", "department": "it_security",
            "start_day": d + 7, "manager": "EMP-0001", "summary": "Privileged role: baseline access only until the "
            "CISO approves admin access"}, sim_time=d),
        bus.make_message("people", "it_security", "people.contractor_engaged", {
            "contractor_id": "CTR-0004", "role": "Data engineer (associate)", "department": "data",
            "engagement_end_day": d + 90, "background_check": True, "summary": "Associate engaged for 90 days"},
            sim_time=d + 1),
        bus.make_message("people", "it_security", "people.employee_left", {
            "employee_id": "EMP-0012", "role": "Senior Consultant", "department": "delivery", "last_day": d + 10,
            "reason_category": "resignation", "involuntary": False, "device_returned": False,
            "summary": "Resignation with 10 days' notice"}, sim_time=d + 4),
        bus.make_message("people", "it_security", "people.employee_left", {
            "employee_id": "EMP-0019", "role": "Platform administrator", "department": "operations",
            "reason_category": "dismissal", "involuntary": True, "privileged": True, "device_returned": True,
            "exfiltration_suspected": True, "summary": "Gross misconduct; bulk document export observed before exit"},
            sim_time=d + 6),
    ]


def scenario_vulnerability_lifecycle(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A release ships with findings, one fixed and verified and one left to breach its SLA (SOP-IT_SECURITY-06).

    Expected chain: product.release_shipped -> it_security.vulnerability_found (product, operations) for each finding
    of medium or above; product.vulnerability_fixed -> verification; the unfixed high finding escalates to the Chief
    Product Officer at 100% of its SLA.
    """
    d = clock.day
    findings = [
        {"vulnerability_id": "VULN-9001", "severity": "critical", "summary": "Remote code execution in the "
         "report-rendering library used by the client portal", "component": "client-portal", "cvss": 9.8,
         "exploited_in_wild": True},
        {"vulnerability_id": "VULN-9002", "severity": "high", "summary": "Missing authorisation check on the agent "
         "run-history endpoint", "component": "agent-platform-api", "cvss": 8.1, "exploited_in_wild": False},
        {"vulnerability_id": "VULN-9003", "severity": "low", "summary": "Verbose error banner", "component": "web",
         "cvss": 3.1},
    ]
    release = {"release_id": params.get("release_id", "REL-2026-014"), "product": "Lumenhall Agent Platform",
               "version": "2.8.0", "change_summary": "Client portal reporting and run-history features",
               "findings": findings}
    fixed = {"vulnerability_id": "VULN-9001", "release_id": release["release_id"],
             "fix_summary": "Library upgraded and render sandbox tightened", "rescan_clean": True}
    return [
        bus.make_message("product", "it_security", "product.release_shipped", release, sim_time=d),
        bus.make_message("product", "it_security", "product.vulnerability_fixed", fixed, sim_time=d + 1),
    ]


def scenario_client_security_review(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Two client security reviews: a large standard questionnaire and a bespoke on-site audit request (SOP-07).

    Expected chain: sales.security_review_requested -> it_security.security_questionnaire_completed (sales, legal)
    after 3 business days (standard) or 4 (bespoke); the 320,000 Forge Build deal needs CISO sign-off (at or above
    250,000).
    """
    d = clock.day
    big = {"deal_id": "DL-0014", "client_id": "CL-0007", "client_name": "Calder Freight Group",
           "questionnaire_type": "sig_lite", "due_day": d + 7, "amount_gbp": params.get("amount_gbp", 320000),
           "data_access_required": True, "certifications_required": ["iso_27001"], "service_line": "forge",
           "tier": "forge_build", "summary": "Procurement security questionnaire before contract"}
    bespoke = {"deal_id": "DL-0015", "client_id": "CL-0011", "client_name": "Fenwick Precision Components",
               "questionnaire_type": "bespoke_on_site_audit", "due_day": d + 10, "amount_gbp": 90000,
               "data_access_required": False, "commitments_requested": ["right_to_audit"], "service_line": "forge",
               "tier": "forge_pilot", "summary": "Client asks for bespoke spreadsheet and an on-site audit"}
    return [
        bus.make_message("sales", "it_security", "sales.security_review_requested", big, sim_time=d),
        bus.make_message("sales", "it_security", "sales.security_review_requested", bespoke, sim_time=d + 2),
    ]


def scenario_vendor_and_ai_risk(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """An AI model vendor is assessed and approved with conditions, plus an AI agent risk review (SOP-08, -10).

    Expected chain: operations.vendor_review_requested -> it_security.vendor_risk_assessed (operations, legal, finance)
    -> operations.vendor_approved -> condition verification; product.ai_risk_review_requested -> register update
    (a secret found in a prompt raises it_security.vulnerability_found).
    """
    d = clock.day
    request = {"vendor_id": "VN-0021", "vendor_name": "Quillstone Model Hosting", "service": "AI model hosting",
               "data_classes": ["client_confidential"], "annual_cost_gbp": 62000, "tier_hint": 2,
               "ai_platform": True, "data_location": "us", "due_day": d + 20, "evidence": ["soc2_type2"]}
    approved = {"vendor_id": "VN-0021", "vendor_name": "Quillstone Model Hosting", "amount_gbp": 62000}
    review = {"agent_id": "AGT-delivery-triage-02", "change_summary": "Supplier-quality triage agent reads client "
              "emails and can raise purchase requests", "client_facing": True, "data_classes": ["client_confidential"],
              "requested_by": "Chief Product Officer", "reads_untrusted_content": True, "secrets_in_prompts": True,
              "write_actions": True, "urgent": True}
    return [
        bus.make_message("operations", "it_security", "operations.vendor_review_requested", request, sim_time=d),
        bus.make_message("operations", "it_security", "operations.vendor_approved", approved, sim_time=d + 12),
        bus.make_message("product", "it_security", "product.ai_risk_review_requested", review, sim_time=d + 1),
    ]


def scenario_compliance_and_budget_cycle(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Regulatory change, policy update, training and continuity evidence, then the annual budget cycle (SOP-09, -11).

    Expected chain: legal.regulatory_change_noted, legal.policy_update_published, people.compliance_training_completed
    and operations.continuity_test_completed feed the certification evidence (monthly
    it_security.certification_status_updated to legal, sales, executive); finance.budget_cycle_opened ->
    it_security.budget_submitted (460,000 FY2026 envelope shape: FY2027 is 920,000); executive.budget_approved.
    """
    d = clock.day
    return [
        bus.make_message("legal", "it_security", "legal.regulatory_change_noted", {
            "regulation": "UK Cyber Security and Resilience requirements update", "effective_day": d + 200,
            "severity": "high", "summary": "New incident reporting duty for managed service providers"}, sim_time=d),
        bus.make_message("legal", "it_security", "legal.policy_update_published", {
            "policy_id": "POL-AI-USE", "version": "3.0", "effective_day": d + 30,
            "summary": "AI tool and agent use policy updated"}, sim_time=d + 1),
        bus.make_message("people", "it_security", "people.compliance_training_completed", {
            "course": "Security awareness and data protection", "completion_rate": 92.0, "cohort": "2026-Q1"},
            sim_time=d + 2),
        bus.make_message("operations", "it_security", "operations.continuity_test_completed", {
            "test_id": "BCP-2026-01", "scenario": "Loss of Google Workspace tenant for 8 hours", "rto_met": False,
            "rpo_met": True, "findings": ["Break-glass account process slower than plan"]}, sim_time=d + 3),
        bus.make_message("finance", "it_security", "finance.budget_cycle_opened", {
            "budget_cycle_id": "BUD-2027", "year": 2027, "due_day": d + 21}, sim_time=d + 5),
        bus.make_message("executive", "it_security", "executive.budget_approved", {
            "year": 2027, "budget_cycle_id": "BUD-2027", "budgets": {"it_security": 920000}}, sim_time=d + 40),
        bus.make_message("executive", "it_security", "executive.okrs_set", {
            "objectives": ["ISO 27001 certified by year end", "Zero ICO-reportable breaches"]}, sim_time=d + 41),
    ]


def scenario_crisis_response(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """The CEO declares a security-driven crisis (ransomware precursor); SOP-IT_SECURITY-03.

    Expected chain: executive.crisis_declared -> it_security.incident_detected (critical) -> later
    it_security.incident_resolved, with the crisis stand-down recorded.
    """
    return [bus.make_message("executive", "it_security", "executive.crisis_declared", {
        "summary": "Ransomware precursor detected on the finance file server; containment under way",
        "severity": "critical", "security_related": True, "expected_duration_days": 5}, sim_time=clock.day)]


SCENARIOS = {
    "phishing_to_breach": scenario_phishing_to_breach,
    "joiner_mover_leaver": scenario_joiner_mover_leaver,
    "vulnerability_lifecycle": scenario_vulnerability_lifecycle,
    "client_security_review": scenario_client_security_review,
    "vendor_and_ai_risk": scenario_vendor_and_ai_risk,
    "compliance_and_budget_cycle": scenario_compliance_and_budget_cycle,
    "crisis_response": scenario_crisis_response,
}
