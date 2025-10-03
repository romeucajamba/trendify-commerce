from loguru import logger
import sys
from pathlib import Path

LOG_PATH = Path("logs")
LOG_PATH.mkdir(exist_ok=True)

# Remove default handler and reconfigure
logger.remove()

# Console
logger.add(sys.stderr, level="INFO", backtrace=True, diagnose=False, enqueue=True)

# File with rotation: 10 MB per file, keep 7 files
logger.add(
    str(LOG_PATH / "app.log"),
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    level="DEBUG",
    backtrace=True,
    enqueue=True,
)