from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from database import users_collection
from models.user import UserRegister, UserLogin, UserOut, TokenOut
from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES

router  = APIRouter(prefix="/api/auth", tags=["auth"])
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer  = HTTPBearer()

def hash_password(pw: str) -> str:
    return pwd_ctx.hash(pw[:72])

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)

def create_token(user_id: str) -> str:
    exp     = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": exp}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        user["id"] = str(user["_id"])
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

@router.post("/register", response_model=TokenOut, status_code=201)
async def register(body: UserRegister):
    existing = await users_collection.find_one({"email": body.email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    doc = {
        "username": body.username,
        "email": body.email,
        "hashed_password": hash_password(body.password),
        "created_at": datetime.now(timezone.utc),
    }
    result  = await users_collection.insert_one(doc)
    user_id = str(result.inserted_id)
    token   = create_token(user_id)
    return TokenOut(access_token=token, user=UserOut(id=user_id, username=body.username, email=body.email))

@router.post("/login", response_model=TokenOut)
async def login(body: UserLogin):
    user = await users_collection.find_one({"email": body.email})
    if not user or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_id = str(user["_id"])
    token   = create_token(user_id)
    return TokenOut(access_token=token, user=UserOut(id=user_id, username=user["username"], email=user["email"]))

@router.get("/me", response_model=UserOut)
async def me(current_user: dict = Depends(get_current_user)):
    return UserOut(id=str(current_user["_id"]), username=current_user["username"], email=current_user["email"])
