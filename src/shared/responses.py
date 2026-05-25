from fastapi.responses import JSONResponse


def success_response(data: dict | list, status_code: int = 200) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=data)


def error_response(detail: str, status_code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})