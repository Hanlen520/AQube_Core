import os


PROJECT_DIR = os.path.dirname(__file__)
WORKSPACE_DIR = os.path.join(PROJECT_DIR, 'workspace')
LOG_FILE = os.path.join(PROJECT_DIR, 'qube.log')


if not os.path.exists(WORKSPACE_DIR):
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
