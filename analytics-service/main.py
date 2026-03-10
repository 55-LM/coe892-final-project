"""
Analytics Service - Entry point.
Reads pickup events from Operations and city data from Planning; computes and exposes metrics.
Part of the distributed Real-Time City Waste Collection Management System.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router


app = FastAPI(
    title="Analytics Service",
    description="Summary metrics, by-neighbourhood and by-waste-type, from pickup events.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api", tags=["analytics"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
