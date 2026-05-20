from __future__ import annotations

import subprocess
import sys


def main() -> None:
    subprocess.run([sys.executable, "deployment/scripts/smoke_test.py"], check=True)


if __name__ == "__main__":
    main()
