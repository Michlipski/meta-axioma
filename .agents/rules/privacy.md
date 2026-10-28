# Universal Privacy & Anonymity Invariant ([NEG-PRIVACY-001])

## Axiomatic Mandate
Under **[NEG-PRIVACY-001]**, all autonomous agents, subagents, compilers, synthesizers, and generators collaborating on Meta-Axioma are strictly prohibited from generating, emitting, or embedding the personal name of the human supervisor/user (including "Michael", "Lipski", or "Michael Lipski") into any generated code, documentation, UI dashboard, HTML, comment, commit message, or telemetry artifact.

## Approved Substitutions
Always use formal, institutional role designations:
- **"The Human Architect"**
- **"Human Systems Architect"**
- **"Principal Systems Architect"**
- **"User Zero"** (when referring to empirical dogfooding and ergonomic verification)
- **"Human Supervisor"** / **"Human Governance Custodian"** (when referring to negative vetoes `NEG-###` or RFC adjudication)

## Enforcement & Zero-Trust Auditing
- Any generated UI component, telemetry trace, documentation file, or code file containing the user's personal name is considered in violation of `[NEG-PRIVACY-001]`.
- Micro-auditors and QA sentries (`test_adversarial_qa.py`, `ZeroTrustMicroAuditor`) must assert that no occurrences of the user's personal name exist in public deliverables or standalone dashboards.
