from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import os
from dotenv import load_dotenv
from app.routes import auth, journal, free_journal, garden
from app.database import create_db_and_tables # Import create_db_and_tables
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

# Call create_db_and_tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# CORS Middleware
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

# Create client_secret.json for Google OAuth
google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

if not google_client_id:
    raise ValueError("GOOGLE_CLIENT_ID environment variable not set.")
if not google_client_secret:
    raise ValueError("GOOGLE_CLIENT_SECRET environment variable not set.")
if not redirect_uri:
    raise ValueError("REDIRECT_URI environment variable not set.")

client_secret_data = {
    "web": {
        "client_id": google_client_id,
        "client_secret": google_client_secret,
        "redirect_uris": [redirect_uri],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
    }
}
with open("client_secret.json", "w") as f:
    json.dump(client_secret_data, f)


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(journal.router, prefix="/journal", tags=["journal"])
app.include_router(free_journal.router, prefix="/freejournal", tags=["free-journal"])
app.include_router(garden.router, prefix="/garden", tags=["garden"])




@app.get("/")
def read_root():
    return {"message": "Welcome to the Journal App"}
