import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# NOW import other modules
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import json
from app.routes import auth, guided_journal as guided_journal_router, free_journal as free_journal_router, garden as garden_router, stats, inference as inference_router
from app.database import create_db_and_tables
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Middleware
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Call create_db_and_tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    
    # Initialize Raindrop service if available
    try:
        from app.services.raindrop_service import raindrop_service
        if raindrop_service.client:
            print("✅ Raindrop service initialized successfully")
            # Optionally check application status
            status = raindrop_service.get_application_status()
            if not status.get("error"):
                print(f"📱 Application '{raindrop_service.application_name}' status: {status.get('is_catalogued', 'Unknown')}")
        else:
            print("⚠️ Raindrop client not available - application may not be catalogued")
    except Exception as e:
        print(f"⚠️ Raindrop service initialization failed: {e}")

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
app.include_router(guided_journal_router.router, prefix="/guided_journal", tags=["guided_journal"])
app.include_router(free_journal_router.router, prefix="/freejournal", tags=["free-journal"])
app.include_router(garden_router.router, prefix="/garden", tags=["garden"])
app.include_router(stats.router, prefix="/stats", tags=["stats"])
app.include_router(inference_router.router, prefix="/inference", tags=["inference"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Guided Journal App"}