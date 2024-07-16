import sys, os

# Add the path to the sys.path
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

### Load Environment Variables - START ###
from dotenv import load_dotenv
load_dotenv()

help_str = """
Required Environment Variables:
- DATABASE_URL: The URL of the SQLite database.
- FTP_SERVER: The Base URL of the FTP server where the files will be uploaded.
- ALLOW_ORIGIN: The list of allowed origins for CORS.
"""

DATABASE_URL = os.getenv('DATABASE_URL')
FTP_SERVER = os.getenv('FTP_SERVER')
ALLOW_ORIGIN = os.getenv('ALLOW_ORIGIN')

if not all([DATABASE_URL, FTP_SERVER, ALLOW_ORIGIN]):
    print(help_str)
    raise ValueError(f'Required environment variables are not set. DATABASE_URL: {DATABASE_URL}, FTP_SERVER: {FTP_SERVER}, ALLOW_ORIGIN: {ALLOW_ORIGIN}')

print(f"DATABASE_URL set to => {DATABASE_URL}")
print(f"FTP_SERVER set to => {FTP_SERVER}")
print(f"ALLOW_ORIGIN set to => {ALLOW_ORIGIN}")
allowed_origin = ALLOW_ORIGIN.split(",")

### Load Environment Variables - END ###

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routes import tasks, home, users
from utils import auth, crud, dependencies, middlewares
import models, schemas
from sqlalchemy.orm import Session
import datetime

# Configure Logger
from utils import log_config
    
# Create the database tables if they do not exist
models.Base.metadata.create_all(bind=dependencies.engine)

app = FastAPI(
    title="Issue Tracker APIs",
    description="A issue tracker API using FastAPI",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "tasks",
            "description": "Operations with tasks.",
        },
        {
            "name": "users",
            "description": "Operations related to users.",
        },
    ],
    swagger_ui_init_oauth={
        "clientId": "your-client-id",
        "usePkceWithAuthorizationCodeGrant": "true",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# configure middlewares
app.add_middleware(middlewares.LoggingMiddleware)

app.include_router(home.router, prefix="/api", tags=["home"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(users.router, prefix="/api/users", tags=["users"])


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(dependencies.get_db)):
    """Get the access token for the user"""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = datetime.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    response = JSONResponse(content={
        "access_token": access_token, 
        "token_type": "bearer", 
        "user": schemas.User(**crud.get_user(db, user.id).__dict__).model_dump()
    })
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite='Strict')
    return response