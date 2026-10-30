"""Password and minimal JWT primitives; secrets are never committed."""
import base64, hashlib, hmac, json, os, secrets
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.orm import Session
from app.database import get_db
from app.platform_models import User

SECRET = os.getenv("JWT_SECRET") or secrets.token_urlsafe(48) # development-only ephemeral secret
hasher = PasswordHasher()
bearer = HTTPBearer(auto_error=False)
def hash_password(value): return hasher.hash(value)
def verify_password(value, encoded):
    try: return hasher.verify(encoded, value)
    except VerifyMismatchError: return False
def _b64(value): return base64.urlsafe_b64encode(value).rstrip(b"=").decode()
def _unb64(value): return base64.urlsafe_b64decode(value + "=" * (-len(value)%4))
def create_token(payload, minutes):
    data = {**payload, "exp": int((datetime.now(timezone.utc)+timedelta(minutes=minutes)).timestamp()), "jti": secrets.token_urlsafe(18)}
    header = _b64(json.dumps({"alg":"HS256","typ":"JWT"}, separators=(",",":")).encode())
    body = _b64(json.dumps(data, separators=(",",":")).encode())
    sig = _b64(hmac.new(SECRET.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest())
    return f"{header}.{body}.{sig}"
def decode_token(token):
    try:
        h,b,s=token.split("."); expected=_b64(hmac.new(SECRET.encode(),f"{h}.{b}".encode(),hashlib.sha256).digest())
        data=json.loads(_unb64(b)); assert hmac.compare_digest(s,expected) and data["exp"] >= datetime.now(timezone.utc).timestamp(); return data
    except Exception: raise HTTPException(status_code=401, detail="Invalid or expired token", headers={"WWW-Authenticate":"Bearer"})
def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    if not credentials: raise HTTPException(status_code=401, detail="Authentication required")
    data=decode_token(credentials.credentials)
    if data.get("typ") != "access": raise HTTPException(status_code=401, detail="Access token required")
    user=db.get(User, data.get("sub"))
    if not user or not user.is_active: raise HTTPException(status_code=401, detail="Account unavailable")
    return user
def require_roles(*roles):
    def check(user=Depends(current_user)):
        if user.role not in roles: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user
    return check
