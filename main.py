"""Group 4 integration entrypoint.

This file now delegates execution to main_model.py, which is the current
Group 4 integration pipeline implementation.
"""

from main_model import main as run_main_model


if __name__ == "__main__":
    run_main_model()
