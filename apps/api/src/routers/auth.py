from datetime import timedelta
from typing import Literal, Optional
from fastapi import Depends, APIRouter, HTTPException, Response, Request
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlmodel import Session
from src.db.users import AnonymousUser, UserRead
from src.core.events.database import get_db_session
from config.config import get_learnhouse_config
from src.security.auth import authenticate_user, get_current_user, create_access_token
from src.services.auth.utils import signWithGoogle
from jose import JWTError, jwt
from src.security.security import ALGORITHM, SECRET_KEY


router = APIRouter()





@router.post("/login")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session: Session = Depends(get_db_session),
):
    user = await authenticate_user(
        request, form_data.username, form_data.password, db_session
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": form_data.username})
    refresh_token = create_access_token(data={"sub": form_data.username}, expires_delta=timedelta(days=7))

    # set cookies using fastapi
    response.set_cookie(
        key="access_token_cookie",
        value=access_token,
        httponly=False,
        domain=get_learnhouse_config().hosting_config.cookie_config.domain,
        expires=int(timedelta(hours=8).total_seconds()),
    )
    
    response.set_cookie(
        key="refresh_token_cookie",
        value=refresh_token,
        httponly=True,
        domain=get_learnhouse_config().hosting_config.cookie_config.domain,
        expires=int(timedelta(days=7).total_seconds()),
    )

    user = UserRead.model_validate(user)

    result = {
        "user": user,
        "tokens": {"access_token": access_token, "refresh_token": refresh_token},
    }
    return result


class ThirdPartyLogin(BaseModel):
    email: EmailStr
    provider: Literal["google"]
    access_token: str


@router.post("/oauth")
async def third_party_login(
    request: Request,
    response: Response,
    body: ThirdPartyLogin,
    org_id: Optional[int] = None,
    current_user: AnonymousUser = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
):
    # Google
    if body.provider == "google":
        user = await signWithGoogle(
            request, body.access_token, body.email, org_id, current_user, db_session
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(days=7))

    # set cookies using fastapi
    response.set_cookie(
        key="access_token_cookie",
        value=access_token,
        httponly=False,
        domain=get_learnhouse_config().hosting_config.cookie_config.domain,
        expires=int(timedelta(hours=8).total_seconds()),
    )
    
    response.set_cookie(
        key="refresh_token_cookie",
        value=refresh_token,
        httponly=True,
        domain=get_learnhouse_config().hosting_config.cookie_config.domain,
        expires=int(timedelta(days=7).total_seconds()),
    )

    user = UserRead.model_validate(user)

    result = {
        "user": user,
        "tokens": {"access_token": access_token, "refresh_token": refresh_token},
    }
    return result


@router.get("/refresh")
async def refresh_token(request: Request, response: Response):
    """
    Refresh access token using refresh token from cookie
    """
    refresh_token = request.cookies.get("refresh_token_cookie")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
        )
    
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    # Create new access token
    access_token = create_access_token(data={"sub": username})
    
    # Set new access token cookie
    response.set_cookie(
        key="access_token_cookie",
        value=access_token,
        httponly=False,
        domain=get_learnhouse_config().hosting_config.cookie_config.domain,
        expires=int(timedelta(hours=8).total_seconds()),
    )
    
    return {"access_token": access_token}


@router.delete("/logout")
def logout(response: Response):
    """
    Because the JWT are stored in an httponly cookie now, we cannot
    log the user out by simply deleting the cookies in the frontend.
    We need the backend to send us a response to delete the cookies.
    """
    response.delete_cookie(
        key="access_token_cookie",
        domain=get_learnhouse_config().hosting_config.cookie_config.domain,
    )
    response.delete_cookie(
        key="refresh_token_cookie", 
        domain=get_learnhouse_config().hosting_config.cookie_config.domain,
    )
    return {"msg": "Successfully logout"}
