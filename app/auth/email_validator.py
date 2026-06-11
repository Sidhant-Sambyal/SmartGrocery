from app.core.config import settings


def is_company_email(email: str) -> bool:
    return email.lower().endswith(
        f"@{settings.COMPANY_DOMAIN.lower()}"
    )