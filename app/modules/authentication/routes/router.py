from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core import security
from app.modules.user.models.users import User
from app.modules.authentication.models.users_auth_token import UserAuthToken, TokenEnum
from app.modules.authentication.schemas.sign_up_schema import SignUpRequest

router = APIRouter(prefix="/auth")

ACCESS_TOKEN_EXPIRY_MINUTES = 5
REFRESH_TOKEN_EXPIRY_DAYS = 7
DEFAULT_USER_TYPE = "5x505"


@router.post('/sign-up')
async def auth_sign_up(signup_request: SignUpRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        User.user_email == signup_request.user_email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already registered",
        )

    now = datetime.utcnow()

    user = User(
        user_email=signup_request.user_email,
        user_type=DEFAULT_USER_TYPE,
        user_password=security.hash_password(signup_request.password),
        created_at=now,
        updated_at=now,
    )
    db.add(user)
    db.flush()

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

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "message": "User registered successfully",
            "data": {}
        }
    )