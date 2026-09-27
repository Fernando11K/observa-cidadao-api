from datetime import UTC, datetime


def em_utc(valor: datetime) -> datetime:
    """O SQLite grava CURRENT_TIMESTAMP em UTC, mas sem fuso horário."""
    return valor if valor.tzinfo else valor.replace(tzinfo=UTC)
