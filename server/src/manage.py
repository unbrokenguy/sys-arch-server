#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path
from file.file_types import FILE_TYPES

PATH_TO_STORAGE = "../files"


def main():
    """Run administrative tasks."""
    for i in FILE_TYPES.keys():
        p = Path(f"{PATH_TO_STORAGE}/{i}")
        p.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
