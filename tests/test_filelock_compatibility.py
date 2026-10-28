"""Offline coverage for the explicitly approved cached-path/filelock override."""

import subprocess
import sys
import zipfile
from pathlib import Path

from cached_path import cached_path
from cached_path.file_lock import FileLock


def test_cached_path_lock_acquires_and_releases(tmp_path: Path) -> None:
    lock = FileLock(tmp_path / "cache.lock", timeout=1)
    with lock:
        assert lock.is_locked
        with lock:
            assert lock.is_locked
    assert not lock.is_locked


def test_cached_path_lock_excludes_another_process(tmp_path: Path) -> None:
    path = tmp_path / "cache.lock"
    script = """
import sys
from cached_path.file_lock import FileLock
from filelock import Timeout
try:
    with FileLock(sys.argv[1], timeout=0.05):
        raise SystemExit(1)
except Timeout:
    raise SystemExit(0)
"""
    with FileLock(path, timeout=1):
        result = subprocess.run([sys.executable, "-c", script, str(path)], timeout=15)
    assert result.returncode == 0


def test_cached_path_extracts_local_archive_and_reuses_cache(tmp_path: Path) -> None:
    archive = tmp_path / "fixture.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("sample.txt", "offline fixture")
    first = cached_path(archive, cache_dir=tmp_path / "cache", extract_archive=True)
    assert (first / "sample.txt").read_text() == "offline fixture"
    second = cached_path(archive, cache_dir=tmp_path / "cache", extract_archive=True)
    assert second == first
