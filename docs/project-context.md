# Project Context

- Project name: `backend-harness-template`
- Product summary: A reusable FastAPI backend with deterministic engineering gates and a report-only Agent loop.
- Primary users: Backend teams adopting an Agent-assisted engineering workflow.
- Core outcome: A normal backend change can be accepted or rejected using reproducible local and CI evidence.
- Data sensitivity: The template contains no production data. Adopting projects must classify their own personal, financial, confidential, and provider data.

## Replace During Adoption

Document:

1. Product users and the concrete outcome the API provides.
2. Trust boundaries and authenticated actors.
3. Authoritative systems of record.
4. Public API compatibility expectations.
5. Data classification, retention, deletion, backup, and recovery requirements.
6. External providers, failure modes, quotas, and idempotency behavior.
7. Service-level objectives and operational ownership.

Do not leave this document as a generic architecture inventory. It should help a new engineer or Agent decide what must not change accidentally.
