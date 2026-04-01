import subprocess
import venv
import os
venv.create("test_venv", with_pip=True)
subprocess.run(["test_venv/bin/pip", "install", "-r", "requirements.txt"])
subprocess.run(["du", "-sh", "test_venv"])
