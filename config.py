import os

# --- pc ---
PROJECT_DIR = os.path.dirname(__file__)
WORKSPACE_DIR = os.path.join(PROJECT_DIR, 'workspace')
EXTEND_DIR = os.path.join(PROJECT_DIR, 'extend')
LOG_FILE = os.path.join(PROJECT_DIR, 'qube.log')

# --- phone ---
TEMP_SHELL_DIR = '/data/local/tmp'

if not os.path.exists(WORKSPACE_DIR):
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
