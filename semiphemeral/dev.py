import os
import subprocess


def build():
    frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
    subprocess.run(["npm", "run", "build"], cwd=frontend_path)
