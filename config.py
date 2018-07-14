import os


PROJECT_DIR = os.path.dirname(__file__)
WORKSPACE_DIR = os.path.join(PROJECT_DIR, 'workspace')


if not os.path.exists(WORKSPACE_DIR):
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
