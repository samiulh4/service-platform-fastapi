from fastapi import APIRouter, Depends, status, HTTPException, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.database import get_db
from app.core import security
from app.core.redis_client import redis_client, _token_key, store_token, get_user_id_from_token, delete_token, delete_user_tokens, store_user, get_user, delete_user
from app.modules.user.models import User
from app.modules.authentication.models import UserAuthToken, TokenEnum
from app.modules.authentication.schemas import SignUpRequest, SignInRequest, SignInResponse, UserResponse

router = APIRouter(prefix="/auth")

ACCESS_TOKEN_EXPIRY_MINUTES = 5
REFRESH_TOKEN_EXPIRY_DAYS = 7
DEFAULT_USER_TYPE = "5x505"
DEFAULT_USER_STATUS = 0


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authorization token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.replace("Bearer ", "")
    #print(f"Authorization token: {token}")

    # Check Redis first for fast validation
    user_id = await get_user_id_from_token(token, "access")
    #print(f"User ID from Redis: {user_id}")
    if user_id:
        # Try to get user data from Redis cache
        cached_user = await get_user(user_id)
        #print(f"Cached user data from Redis: {cached_user}")
        if cached_user:
            return User(**cached_user)

        # User not cached, query DB and cache for future requests
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            ttl = await redis_client.ttl(_token_key(token, "access"))
            if ttl > 0:
                user_data = {c.name: getattr(user, c.name) for c in User.__table__.columns if c.name != "user_password"}
                await store_user(user_id, user_data, ttl)
            return user

    # Fallback to DB query
    auth_token = db.query(UserAuthToken).filter(
        UserAuthToken.token == token,
        UserAuthToken.type == TokenEnum.access,
        UserAuthToken.status == 1,
        UserAuthToken.expires_at > datetime.now(timezone.utc)
    ).first()

    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Cache token in Redis for future requests
    ttl = int((auth_token.expires_at - datetime.now(timezone.utc)).total_seconds())
    if ttl > 0:
        await store_token(token, auth_token.user_id, "access", ttl)

    user = db.query(User).filter(User.id == auth_token.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Cache user data in Redis
    user_data = {c.name: getattr(user, c.name) for c in User.__table__.columns if c.name != "user_password"}
    await store_user(user.id, user_data, ttl)

    return user


@router.post('/sign-up')
async def auth_sign_up(signup_request: SignUpRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        User.user_identity == signup_request.identity
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already registered",
        )
    
    now = datetime.now(timezone.utc)

    user = User(
        user_identity  = signup_request.identity,
        user_full_name = signup_request.name,
        user_email     = signup_request.email,
        user_mobile    = signup_request.mobile,
        user_gender    = signup_request.gender,
        user_birthday  = signup_request.birthday,
        user_status    = DEFAULT_USER_STATUS,
        user_password  = security.hash_password(signup_request.password),
        user_type      = DEFAULT_USER_TYPE,
        created_at     = now,
        updated_at     = now,
    )
    db.add(user)
    db.flush()
    db.commit()

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "message": "User registered successfully",
            "data": {}
        }
    )


@router.post('/sign-in', response_model=SignInResponse)
async def auth_sign_in(signin_request: SignInRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.user_identity == signin_request.identity
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid identity or password",
        )

    if not security.verify_password(signin_request.password, user.user_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid identity or password",
        )

    now = datetime.now(timezone.utc)

    access_token = security.generate_token()
    refresh_token = security.generate_token()

    db.add_all([
        UserAuthToken(
            token=access_token,
            type=TokenEnum.access,
            status=1,
            user_id=user.id,
            expires_at=now + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES),
            created_at=now,
            updated_at=now,
        ),
        UserAuthToken(
            token=refresh_token,
            type=TokenEnum.refresh,
            status=1,
            user_id=user.id,
            expires_at=now + timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS),
            created_at=now,
            updated_at=now,
        ),
    ])

    db.commit()

    # Store tokens in Redis with TTL
    await store_token(access_token, user.id, "access", ACCESS_TOKEN_EXPIRY_MINUTES * 60)
    await store_token(refresh_token, user.id, "refresh", REFRESH_TOKEN_EXPIRY_DAYS * 86400)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Login successful",
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "refresh_token": refresh_token,
            }
        }
    )


@router.get('/me', response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post('/sign-out')
async def sign_out(
    current_user: User = Depends(get_current_user),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    token = authorization.replace("Bearer ", "")

    # Delete access token from Redis
    await delete_token(token, "access")

    # Invalidate all tokens for this user in DB
    db.query(UserAuthToken).filter(
        UserAuthToken.user_id == current_user.id,
        UserAuthToken.status == 1,
    ).update({UserAuthToken.status: 0, UserAuthToken.updated_at: datetime.now(timezone.utc)})
    db.commit()

    # Delete all user tokens and user data from Redis
    await delete_user_tokens(current_user.id)
    await delete_user(current_user.id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"success": True, "message": "Signed out successfully"}
    )
