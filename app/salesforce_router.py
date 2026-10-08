"""Explicit opt-in read-only Salesforce integration; no write endpoints."""
import os
from fastapi import APIRouter, HTTPException
from app.salesforce_azure import SalesforceConfig, SalesforceReadClient
router=APIRouter(prefix='/integrations/salesforce', tags=['Salesforce Azure adapter'])

@router.get('/accounts/{account_id}')
async def account(account_id: str):
    # Intentionally disabled unless an identity-aware gateway is deployed.
    if os.getenv('ENABLE_SALESFORCE_READ_API') != 'true':
        raise HTTPException(404, 'Salesforce adapter disabled')
    # Defense-in-depth: this demo endpoint is not suitable for direct public access.
    if os.getenv('GATEWAY_AUTH_ENFORCED') != 'true':
        raise HTTPException(503, 'Authenticated gateway required')
    try:
        return await SalesforceReadClient(SalesforceConfig.from_env()).get_account(account_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
