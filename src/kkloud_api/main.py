from fastapi import FastAPI
from fastapi import status
from .routers.api import router


app = FastAPI(title="KKloud API", version="1.0.0", description="API for KKloud services")
app.include_router(router)


@app.get("/", status_code=status.HTTP_403_FORBIDDEN, description="Root endpoint is forbidden")
async def root():
    return {"message": "Access to the root endpoint is forbidden. Please use /api/v1 for API access."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
