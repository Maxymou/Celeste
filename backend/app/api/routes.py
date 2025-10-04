from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/calc/span")
def calculate_span_placeholder() -> dict[str, str]:
    return {"detail": "Span calculation endpoint placeholder"}
