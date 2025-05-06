import subprocess

import pytest

from flake8_diff_only.utils import get_changed_lines


@pytest.fixture
def patched_get_changed_lines(monkeypatch: pytest.MonkeyPatch):

    def make_checker(diff_output: str):
        monkeypatch.setattr(
            subprocess, "check_output", lambda *args, **kwargs: diff_output.encode()
        )

        return get_changed_lines("test_file.py")

    return make_checker


def test_load_git_diff_parsing(patched_get_changed_lines):
    diff_output = """\
diff --git a/test_file.py b/test_file.py
index e69de29..4b825dc 100644
--- a/test_file.py
+++ b/test_file.py
@@ -0,0 +1,3 @@
+print("Hello")
+print("World")
+print("!")
"""
    result = patched_get_changed_lines(diff_output)

    assert result == {1, 2, 3}, "Ожидались изменённые строки 1, 2 и 3"


def test_diff_single_line_no_comma(patched_get_changed_lines):
    diff_output = """\
diff --git a/test.py b/test.py
index 123..456 100644
--- a/test.py
+++ b/test.py
@@ -4 +45 @@
+print("single")
"""
    result = patched_get_changed_lines(diff_output)
    assert result == {45}, "Ожидалась только строка 45"


def test_diff_header_parse_error(patched_get_changed_lines):
    diff_output = """\
diff --git a/f.py b/f.py
index 123..456 100644
--- a/f.py
+++ b/f.py
@@ nonsense header @@
+print("broken")
"""
    result = patched_get_changed_lines(diff_output)
    assert result == set(), "Файл с некорректным заголовком не должен попадать"


def test_diff_empty(patched_get_changed_lines):
    diff_output = ""
    result = patched_get_changed_lines(diff_output)
    assert result == set()
