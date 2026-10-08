# Enterprise Agent Observability Platform — v1.0

**Azure Container Apps · LangGraph · Azure PostgreSQL Flexible Server · Entra ID · Salesforce Apex · Jira Groovy · ServiceNow · OpenTelemetry · Grafana · Dynatrace**

## New in v1.0
A **new authenticated `/v1` governed-agent API** combines LangGraph checkpointed interrupts, a simulated Customer Risk Assessment, approval/rejection, PostgreSQL audit events and Microsoft Entra JWT verification. This extends the v0.9 repository; earlier labs, Apex/Groovy/ServiceNow examples, Terraform and observability configuration remain included.

**Security and maturity statement:** The v1 flow is a functional integration scaffold, **not production-ready**. The evidence is deterministic fixture data; actions are simulated, not sent to Salesforce, Jira or ServiceNow. Entra must be configured for the new endpoints. The older demo routes retain their earlier authentication limitations and must not be exposed publicly. PostgreSQL checkpoint and audit persistence require an actual database and initialization. No real Azure deployment or SaaS integration has been verified.

## Quick start
Read [v1.0 Runbook](docs/V10_RUNBOOK.md) and [Architecture / Threat Model](docs/V10_ARCHITECTURE.md).

```bash
cp .env.example .env
# Configure ENTRA_TENANT_ID and ENTRA_API_AUDIENCE
docker compose -f docker-compose.yml -f docker-compose.v1.yml up --build -d
```

## API
- `POST /v1/runs` — requires `Agent.Operator` Entra app role; checkpoints at human approval.
- `POST /v1/runs/{run_id}/decision` — requires `Agent.Approver`; resumes the graph.
- `GET /v1/runs/{run_id}` — requires `Agent.Auditor`; state + audit timeline.

## Testing
`pytest -q tests/test_v1_contracts.py` runs unit contract tests; see runbook for PostgreSQL/Entra integration checks. Do not equate passing unit tests with end-to-end validation.

## Next milestone
Transactional outbox, one-time approvals, managed identity for PostgreSQL, real connectors behind the governed Tool Gateway, Azure API Management + Entra enforcement and end-to-end distributed traces.
