from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.api.routes.clientes_routes import router as clientes_router
from src.api.routes.webhooks_routes import router as webhooks_router
from src.api.routes.health_routes import router as health_router
from src.database.init_db import init_db
from src.shared.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up: initializing database...")
    init_db()
    logger.info("Application ready.")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Mundo Invest - Client Management",
    description=(
        "API backend simulando o sistema interno do Mundo Invest para cadastro "
        "de clientes e integração com Pipefy via GraphQL (mocked)."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(clientes_router)
app.include_router(webhooks_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = exc.errors()
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": details,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )