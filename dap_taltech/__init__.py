"""dap_taltech."""
import logging
from pathlib import Path

BUCKET_NAME = "dap-taltech"
PUBLIC_DATA_FOLDER_NAME = "data"

PROJECT_DIR = Path(__file__).resolve().parents[1]

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    bold_yellow = "\x1b[33;20;1;1m"
    bold_red = "\x1b[31;1m"
    bold_blue = "\x1b[94;1;1m"
    reset = "\x1b[0m"
    format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: bold_blue + format + reset,
        logging.WARNING: bold_yellow + format + reset,
        logging.ERROR: bold_red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger(
    "TalTech HackWeek 2023"
)  

logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())
if logger.hasHandlers():
    logger.handlers.clear()
logger.addHandler(ch)
logger.propagate = False