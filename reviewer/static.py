import subprocess
import tempfile
import os
from typing import List, Tuple

def run_flake8(file_path: str) -> List[Tuple[int, str]]:
    """
    Run flake8 on a given Python file and return list of (line, message).
    If file_path is a .patch file, we extract the modified files first.
    For simplicity, this version expects a direct .py file.
    """
    if not file_path.endswith('.py'):
        # For demo, we assume the diff is already applied; we extract the changed file name from the patch.
        # A production version would apply the patch to a temporary repo copy.
        # For simplicity we'll skip static analysis for patch files unless we apply them.
        # We'll implement a basic approach: if the diff is provided, we extract the filename from the diff header.
        # This is a placeholder – we recommend testing on actual .py files or applying the patch.
        print("Warning: flake8 static analysis only works on .py files. Skipping static checks.")
        return []
    try:
        result = subprocess.run(
            ['flake8', file_path, '--format=%(row)d:%(col)d %(code)s %(text)s'],
            capture_output=True, text=True, check=False
        )
        issues = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            # parse line like "10:5 E501 line too long"
            parts = line.split(' ', 1)
            if len(parts) == 2:
                loc, msg = parts
                line_no = loc.split(':')[0]
                try:
                    issues.append((int(line_no), msg))
                except ValueError:
                    pass
        return issues
    except FileNotFoundError:
        print("flake8 not installed or not in PATH. Install with: pip install flake8")
        return []