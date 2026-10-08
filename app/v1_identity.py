"""Verify Entra access tokens using published OIDC signing keys (never trust caller identity headers)."""
import os
from dataclasses import dataclass
from functools import lru_cache
import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, Header

@dataclass(frozen=True)
class Principal:
    subject: str
    tenant: str
    roles: frozenset[str]

@lru_cache(maxsize=4)
def jwks_client(url: str):
    return PyJWKClient(url, cache_jwk_set=True, lifespan=300)

def verify_token(token: str) -> Principal:
    tenant = os.environ.get('ENTRA_TENANT_ID', '')
    audience = os.environ.get('ENTRA_API_AUDIENCE', '')
    if not tenant or not audience:
        raise HTTPException(503, 'Entra configuration missing')
    if tenant in ('common','organizations','consumers'):
        raise HTTPException(503, 'A dedicated Entra tenant is required')
    issuer = f'https://login.microsoftonline.com/{tenant}/v2.0'
    jwks_url = f'https://login.microsoftonline.com/{tenant}/discovery/v2.0/keys'
    try:
        key = jwks_client(jwks_url).get_signing_key_from_jwt(token).key
        claims = jwt.decode(token,key,algorithms=['RS256'],audience=audience,issuer=issuer,
                            options={'require':['exp','iat','iss','aud','tid','oid']},leeway=30)
    except (jwt.PyJWTError, ValueError, KeyError) as exc:
        raise HTTPException(401, 'Invalid bearer token') from exc
    if claims['tid'] != tenant:
        raise HTTPException(403, 'Tenant mismatch')
    return Principal(subject=claims['oid'],tenant=claims['tid'],
                     roles=frozenset(claims.get('roles', [])))

def require_principal(authorization: str = Header(default='')) -> Principal:
    if not authorization.startswith('Bearer '):
        raise HTTPException(401, 'Bearer token required')
    return verify_token(authorization[7:])

def require_role(principal: Principal, role: str):
    if role not in principal.roles:
        raise HTTPException(403, f'{role} application role required')
