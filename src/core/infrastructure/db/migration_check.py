import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def _parse_revision_lines(output):
    """Extract revision id from alembic output (current or heads)."""
    # Ищет строчки вида 'Rev: xxxxxxxxxxxxxxxx' или 'Current revision for ...: xxxxxxxxxxxxxxxx'
    ids = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        # Обычно ревизии идут в начале строки и имеют вид хэша
        if len(line) >= 12 and all(c in "0123456789abcdef" for c in line[:12]):
            ids.append(line.split()[0])
        # Либо форматы типа 'Current revision for ...: xxxxxxxxxxxxxxxx'
        elif "Current revision" in line and ":" in line:
            ids.append(line.split(":")[-1].strip())
        elif "head" in line:  # иногда вместо ревизии пишет 'head'
            continue
    return set(ids)

def check_migrations():
    """Check if all alembic migrations are applied (sync version)."""
    try:
        project_root = Path(__file__).resolve().parent.parent.parent.parent.parent

        # Проверяем наличие alembic
        res = subprocess.run(["alembic", "--version"], capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError("Alembic is not installed or not in PATH.")

        # Получаем текущие применённые ревизии
        current = subprocess.run(
            ["alembic", "current"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        if current.returncode != 0:
            raise RuntimeError(f"Alembic current failed: {current.stderr}")

        # Получаем актуальные head ревизии
        heads = subprocess.run(
            ["alembic", "heads"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        if heads.returncode != 0:
            raise RuntimeError(f"Alembic heads failed: {heads.stderr}")

        # Разбираем выводы
        current_ids = _parse_revision_lines(current.stdout)
        head_ids = _parse_revision_lines(heads.stdout)

        # Диагностика
        if not head_ids:
            logger.warning("No migration heads found. Migrations might not be set up correctly.")
            return False
        if not current_ids:
            logger.error("No migrations have been applied yet. Please run 'alembic upgrade head'.")
            return False

        if current_ids != head_ids:
            logger.error(
                f"Database migrations are not up-to-date!\n"
                f"Current: {current_ids}\n"
                f"Heads: {head_ids}\n"
                "Run: alembic upgrade head"
            )
            return False

        logger.info("✅ Database migrations are up-to-date.")
        return True

    except Exception as e:
        logger.error(f"Error checking migrations: {e}")
        return False
