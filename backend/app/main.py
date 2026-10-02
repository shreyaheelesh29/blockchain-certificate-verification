from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes.auth import router as auth_router
from app.routes.certificate import router as certificate_router
from app.routes.verification import router as verification_router

app = FastAPI(
    title="Certificate Verification System",
    description="Blockchain-Based Certificate Verification System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://192.168.43.225:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated certificate PDFs
app.mount(
    "/generated-certificates",
    StaticFiles(directory="generated/certificates"),
    name="generated-certificates"
)

app.include_router(auth_router)
app.include_router(certificate_router)
app.include_router(verification_router)

@app.get("/")
def root():
    return {
        "message": "Certificate Verification System Backend Running"
    }