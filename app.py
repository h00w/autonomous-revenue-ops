import json
import uuid
import gradio as gr

from src.models import LeadInput, Qualification
from src.policy import evaluate_policy


def run_demo(name, email, company, role, source, message, consent, score, confidence, icp_fit, intent, urgency, risk_flags):
    lead = LeadInput(
        lead_id=f"lead_{uuid.uuid4().hex[:10]}",
        name=name,
        email=email,
        company=company,
        role=role or None,
        source=source,
        message=message,
        consent_to_contact=consent,
    )
    flags = [x.strip() for x in (risk_flags or "").split(",") if x.strip()]
    qualification = Qualification(
        score=int(score),
        confidence=float(confidence),
        icp_fit=int(icp_fit),
        intent=int(intent),
        urgency=int(urgency),
        risk_flags=flags,
        evidence=["Synthetic reviewer input"],
    )
    policy = evaluate_policy(lead, qualification)
    trace = {
        "event_id": f"evt_{uuid.uuid4().hex[:12]}",
        "correlation_id": f"corr_{uuid.uuid4().hex[:12]}",
        "lead": lead.model_dump(mode="json"),
        "qualification": qualification.model_dump(mode="json"),
        "policy": policy.model_dump(mode="json"),
    }
    return policy.decision.value, policy.reason, policy.next_action, json.dumps(trace, indent=2)


with gr.Blocks(title="Autonomous Revenue Ops") as demo:
    gr.Markdown("""
# Autonomous Revenue Ops
**Production-grade AI workflow proof:** structured qualification → deterministic authorization → bounded action.

This demo does **not** let an LLM directly execute business actions. Reviewer-provided qualification values simulate the AI output, while the policy engine determines what is authorized.
""")
    with gr.Row():
        with gr.Column():
            name = gr.Textbox(label="Lead name", value="Jane Doe")
            email = gr.Textbox(label="Email", value="jane@example.com")
            company = gr.Textbox(label="Company", value="Example SaaS AB")
            role = gr.Textbox(label="Role", value="VP Engineering")
            source = gr.Dropdown(["website", "webinar", "partner", "referral", "import"], value="website", label="Source")
            message = gr.Textbox(label="Inbound message", value="We are evaluating automation for our sales operations.")
            consent = gr.Checkbox(label="Consent to contact", value=True)
        with gr.Column():
            score = gr.Slider(0, 100, value=87, step=1, label="Qualification score")
            confidence = gr.Slider(0, 1, value=0.91, step=0.01, label="Confidence")
            icp_fit = gr.Slider(0, 100, value=90, step=1, label="ICP fit")
            intent = gr.Slider(0, 100, value=82, step=1, label="Intent")
            urgency = gr.Slider(0, 100, value=70, step=1, label="Urgency")
            risk_flags = gr.Textbox(label="Risk flags (comma separated)", placeholder="e.g. regulated_data, ambiguous_identity")
    run = gr.Button("Evaluate workflow", variant="primary")
    with gr.Row():
        decision = gr.Textbox(label="Policy decision")
        reason = gr.Textbox(label="Reason")
    next_action = gr.Textbox(label="Authorized next action")
    trace = gr.Code(label="Audit trace", language="json")
    run.click(run_demo, [name, email, company, role, source, message, consent, score, confidence, icp_fit, intent, urgency, risk_flags], [decision, reason, next_action, trace])
    gr.Markdown("""
## Evidence surfaces
- GitHub: https://github.com/h00w/autonomous-revenue-ops
- Dataset: https://huggingface.co/datasets/h0000w/autonomous-revenue-ops
- Model/system card: https://huggingface.co/h0000w/autonomous-revenue-ops

**Maturity:** portfolio-tested / production-candidate architecture. Real production validation requires live CRM credentials, monitoring, incident history, privacy review, and measured business outcomes.
""")

if __name__ == "__main__":
    demo.launch()
