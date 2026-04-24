import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from backend.routers import todo
from backend import database

app = FastAPI(title="Todo API", version="1.0.0")

# Middleware order: 1) Exception handler, 2) Any future middlewares (e.g., CORS)
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        # Convert any unexpected exception to an HTTPException
        raise HTTPException(status_code=500, detail=str(exc))

# Startup and shutdown events to manage SQLite connection
@app.on_event("startup")
async def on_startup():
    await database.connect(app)

@app.on_event("shutdown")
async def on_shutdown():
    await database.disconnect(app)

# Register routers
app.include_router(todo.router)
