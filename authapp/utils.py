import jwt
import uuid
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from .models import RefreshToken
from django.utils import timezone as dj_timezone

JWT_SETTINGS = settings.JWT
ALGO = JWT_SETTINGS.get('ALGORITHM', 'HS256')
ACCESS_LIFE = JWT_SETTINGS.get('ACCESS_TOKEN_LIFETIME_SECONDS', 15 * 60)
REFRESH_LIFE = JWT_SETTINGS.get('REFRESH_TOKEN_LIFETIME_SECONDS', 7 * 24 * 3600)
SECRET = settings.SECRET_KEY

def _now_ts():
    return int(datetime.now(tz=timezone.utc).timestamp())

def create_access_token(user):
    now = datetime.now(tz=timezone.utc)
    exp = now + timedelta(seconds=ACCESS_LIFE)
    jti = str(uuid.uuid4())
    payload = {
        'user_id': user.id,
        'username': getattr(user, 'username', ''),
        'exp': int(exp.timestamp()),
        'iat': int(now.timestamp()),
        'type': 'access',
        'jti': jti,
        'iss': JWT_SETTINGS.get('ACCESS_TOKEN_ISSUER', 'jwtauth_project')
    }
    token = jwt.encode(payload, SECRET, algorithm=ALGO)
    return token, payload

def create_refresh_token(user, rotated_from_jti=None):
    """
    Generates a new refresh token (raw string) and stores its hash in DB.
    Returns raw refresh token and DB entry.
    """
    now = datetime.now(tz=timezone.utc)
    exp = now + timedelta(seconds=REFRESH_LIFE)
    jti = str(uuid.uuid4())
    payload = {
        'user_id': user.id,
        'exp': int(exp.timestamp()),
        'iat': int(now.timestamp()),
        'type': 'refresh',
        'jti': jti,
        'iss': JWT_SETTINGS.get('REFRESH_TOKEN_ISSUER', 'jwtauth_project-refresh')
    }
    raw_token = jwt.encode(payload, SECRET, algorithm=ALGO)
    # hash the raw token BEFORE storing
    token_hash = make_password(raw_token)
    rt = RefreshToken.objects.create(
        user=user,
        jti=jti,
        token_hash=token_hash,
        expires_at=exp,
        rotated_from=rotated_from_jti,
    )
    return raw_token, rt

def decode_token(token, verify_exp=True):
    options = {'verify_exp': verify_exp}
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO], options=options)
        return payload
    except jwt.ExpiredSignatureError:
        raise
    except jwt.InvalidTokenError:
        raise

def verify_refresh_token_in_db(raw_token, payload_jti):
    """
    Ensure the refresh token exists in DB, not revoked, not expired, and hash matches.
    raw_token: the raw JWT refresh token string provided by client
    payload_jti: jti value extracted from decoded token
    """
    try:
        rt = RefreshToken.objects.get(jti=payload_jti)
    except RefreshToken.DoesNotExist:
        return None 

    
    if rt.revoked:
        return None
    
    if rt.is_expired():
        return None
    
    if not check_password(raw_token, rt.token_hash):
        
        return None
    return rt

def revoke_refresh_token(rt: RefreshToken):
    rt.revoked = True
    rt.save(update_fields=['revoked'])
