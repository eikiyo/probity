"""
Location: probity_cli/__main__.py
Purpose: `python -m probity_cli` entry point (mirrors the probity-bench console script).
Functions: (none)
Calls: probity_cli.cli.main
Imports: sys, probity_cli.cli
"""

import sys

from probity_cli.cli import main

if __name__ == "__main__":
    sys.exit(main())
