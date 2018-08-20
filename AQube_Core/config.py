import os
import logging
from pythonjsonlogger import jsonlogger


# --- pc ---
PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
WORKSPACE_DIR = os.path.join(PROJECT_DIR, 'workspace')
EXTEND_DIR = os.path.join(PROJECT_DIR, 'extend')
LOG_FILE = os.path.join(PROJECT_DIR, 'qube.log')

# --- phone ---
TEMP_SHELL_DIR = '/data/local/tmp'

if not os.path.exists(WORKSPACE_DIR):
    os.makedirs(WORKSPACE_DIR, exist_ok=True)


# init logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=LOG_FILE,
    filemode="a",
)

ch = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
ch.setFormatter(formatter)
ch.setLevel(logging.INFO)

logging.getLogger("").addHandler(ch)

__all__ = [
    'PROJECT_DIR',
    'WORKSPACE_DIR',
    'EXTEND_DIR',
    'LOG_FILE',
    'TEMP_SHELL_DIR',
]
